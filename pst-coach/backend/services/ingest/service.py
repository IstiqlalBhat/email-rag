import os
import shutil
import uuid
import json
import re
import hashlib
import subprocess
import email
from email import policy
from email.parser import BytesParser
from datetime import datetime
from pathlib import Path
from fastapi import BackgroundTasks
from loguru import logger
from core.config import settings

# In-memory cache to track indexed uploads (for MVP - use DB in production)
_indexed_uploads = set()

def clean_body(text: str) -> str:
    """Clean email body text."""
    if not text:
        return ""
    # Remove Carriage Returns
    text = re.sub(r"\r\n", "\n", text)
    # Collapse multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove common Outlook forwarding headers (simple heuristic)
    text = re.sub(r"From:.*?\nSent:.*?\nTo:.*?\nSubject:.*?\n", "", text, flags=re.DOTALL)
    text = re.sub(r"_{10,}", "", text) # Remove separator lines
    return text.strip()


def parse_emails_from_blob(content: str) -> list:
    """
    Parse individual emails from a large text blob.
    Uses common email header patterns to split emails.
    """
    emails = []
    
    if not content:
        return emails
    
    # Pattern to match email headers (From: ... Sent: ... To: ... Subject: ...)
    # This handles common Outlook export formats
    email_pattern = re.compile(
        r'(?:^|\n)(?:From:\s*(.+?)(?:\n|$))'
        r'(?:Sent:\s*(.+?)(?:\n|$))?'
        r'(?:To:\s*(.+?)(?:\n|$))?'
        r'(?:Cc:\s*(.+?)(?:\n|$))?'
        r'(?:Subject:\s*(.+?)(?:\n|$))',
        re.MULTILINE | re.IGNORECASE
    )
    
    # Alternative pattern for different email formats
    alt_pattern = re.compile(
        r'(?:^|\n)-{3,}.*?(?:\n|$)'  # Separator lines
        r'|(?:^|\n)From:.*?(?:\n\n|\n(?=From:))',
        re.MULTILINE | re.DOTALL
    )
    
    # Try to split by "From:" headers which typically start emails
    from_splits = re.split(r'\n(?=From:\s*[^\n]+\n)', content)
    
    for i, section in enumerate(from_splits):
        if len(section.strip()) < 50:  # Skip very short sections
            continue
            
        # Extract metadata from the section
        from_match = re.search(r'From:\s*(.+?)(?:\n|$)', section, re.IGNORECASE)
        sent_match = re.search(r'Sent:\s*(.+?)(?:\n|$)', section, re.IGNORECASE)
        date_match = re.search(r'Date:\s*(.+?)(?:\n|$)', section, re.IGNORECASE)
        to_match = re.search(r'To:\s*(.+?)(?:\n|$)', section, re.IGNORECASE)
        subject_match = re.search(r'Subject:\s*(.+?)(?:\n|$)', section, re.IGNORECASE)
        
        # Get the body (everything after the headers)
        body = section
        # Remove header lines from body
        body = re.sub(r'^From:.*?\n', '', body, flags=re.IGNORECASE | re.MULTILINE)
        body = re.sub(r'^Sent:.*?\n', '', body, flags=re.IGNORECASE | re.MULTILINE)
        body = re.sub(r'^Date:.*?\n', '', body, flags=re.IGNORECASE | re.MULTILINE)
        body = re.sub(r'^To:.*?\n', '', body, flags=re.IGNORECASE | re.MULTILINE)
        body = re.sub(r'^Cc:.*?\n', '', body, flags=re.IGNORECASE | re.MULTILINE)
        body = re.sub(r'^Subject:.*?\n', '', body, flags=re.IGNORECASE | re.MULTILINE)
        body = clean_body(body)
        
        if len(body) < 20:  # Skip emails with very short bodies
            continue
        
        email_data = {
            "subject": subject_match.group(1).strip() if subject_match else f"Email {i+1}",
            "from": from_match.group(1).strip() if from_match else "Unknown Sender",
            "to": to_match.group(1).strip() if to_match else "Unknown",
            "date": (sent_match.group(1) if sent_match else 
                    date_match.group(1) if date_match else 
                    str(datetime.now())).strip(),
            "body": body,
            "email_id": hashlib.md5(f"{from_match.group(1) if from_match else ''}{subject_match.group(1) if subject_match else ''}{body[:100]}".encode()).hexdigest()
        }
        emails.append(email_data)
    
    # If no emails found with headers, try splitting by common separators
    if len(emails) == 0:
        # Split by separator patterns (like "-----Original Message-----")
        separator_splits = re.split(r'\n-{5,}.*?-{5,}\n', content)
        
        for i, section in enumerate(separator_splits):
            section = clean_body(section)
            if len(section) < 50:
                continue
                
            emails.append({
                "subject": f"Message {i+1}",
                "from": "PST Import",
                "to": "Unknown",
                "date": str(datetime.now()),
                "body": section,
                "email_id": hashlib.md5(section[:200].encode()).hexdigest()
            })
    
    # If still no emails, treat as one large document but chunk it
    if len(emails) == 0 and len(content) > 100:
        # Split into ~2000 char chunks with overlap
        chunk_size = 2000
        overlap = 200
        
        for i in range(0, len(content), chunk_size - overlap):
            chunk = content[i:i + chunk_size]
            if len(chunk) < 100:
                continue
                
            emails.append({
                "subject": f"PST Content Chunk {i // (chunk_size - overlap) + 1}",
                "from": "PST Import",
                "to": "Unknown", 
                "date": str(datetime.now()),
                "body": clean_body(chunk),
                "email_id": hashlib.md5(chunk.encode()).hexdigest()
            })
    
    return emails


def check_if_already_indexed(upload_id: str) -> bool:
    """Check if this upload has already been indexed."""
    # Check if extracted JSON exists
    output_file = os.path.join(settings.EXTRACTED_DIR, f"{upload_id}.json")
    if os.path.exists(output_file):
        logger.info(f"Upload {upload_id} already has extracted data")
        return True
    return False


def get_existing_upload_ids() -> list:
    """Get list of already processed upload IDs."""
    if not os.path.exists(settings.EXTRACTED_DIR):
        return []
    
    upload_ids = []
    for filename in os.listdir(settings.EXTRACTED_DIR):
        if filename.endswith('.json'):
            upload_ids.append(filename.replace('.json', ''))
    return upload_ids


def get_email_body(msg) -> str:
    """Extract the body from an email message, preferring plain text."""
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            # Skip attachments
            if "attachment" in content_disposition:
                continue

            if content_type == "text/plain":
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        body = payload.decode(charset, errors='replace')
                        break  # Prefer plain text
                except Exception:
                    continue
            elif content_type == "text/html" and not body:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        html_body = payload.decode(charset, errors='replace')
                        # Simple HTML stripping
                        body = re.sub(r'<[^>]+>', ' ', html_body)
                        body = re.sub(r'\s+', ' ', body).strip()
                except Exception:
                    continue
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or 'utf-8'
                body = payload.decode(charset, errors='replace')
        except Exception:
            body = str(msg.get_payload())

    return clean_body(body)


def parse_eml_file(eml_path: str) -> dict:
    """Parse a single .eml file and extract structured data."""
    try:
        with open(eml_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)

        # Extract fields
        subject = msg.get('Subject', 'No Subject') or 'No Subject'
        from_addr = msg.get('From', 'Unknown Sender') or 'Unknown Sender'
        to_addr = msg.get('To', '') or ''
        cc_addr = msg.get('Cc', '') or ''
        date_str = msg.get('Date', '') or ''

        # Get body
        body = get_email_body(msg)

        # Create unique ID
        email_id = hashlib.md5(f"{from_addr}{subject}{body[:100]}".encode()).hexdigest()

        return {
            "subject": str(subject),
            "from": str(from_addr),
            "to": str(to_addr),
            "cc": str(cc_addr),
            "date": str(date_str),
            "body": body,
            "email_id": email_id
        }
    except Exception as e:
        logger.error(f"Error parsing {eml_path}: {e}")
        return None


def process_pst_file(file_path: str, upload_id: str, force_reprocess: bool = False):
    """
    Background task to process a PST file using readpst.
    Extracts individual emails and indexes them.
    """
    logger.info(f"Starting processing for file: {file_path}")

    # Check if already processed
    output_file = os.path.join(settings.EXTRACTED_DIR, f"{upload_id}.json")
    if os.path.exists(output_file) and not force_reprocess:
        logger.info(f"Upload {upload_id} already processed. Skipping extraction.")
        # Still trigger indexing in case it failed before
        from services.index.service import index_messages
        index_messages(upload_id)
        return

    # Create temp directory for extraction
    extract_dir = os.path.join(settings.DATA_DIR, "temp_extract", upload_id)
    os.makedirs(extract_dir, exist_ok=True)

    try:
        # Use readpst to extract emails as .eml files
        # -e = save as .eml format
        # -o = output directory
        # -q = quiet
        logger.info(f"Running readpst to extract emails from PST...")
        result = subprocess.run(
            ["readpst", "-e", "-o", extract_dir, file_path],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )

        if result.returncode != 0:
            logger.error(f"readpst failed: {result.stderr}")
            # Fall back to Tika if available
            logger.info("Falling back to Tika parser...")
            process_pst_with_tika(file_path, upload_id, output_file)
            return

        logger.info(f"readpst completed: {result.stdout}")

        # Find all .eml files recursively
        emails = []
        eml_files = list(Path(extract_dir).rglob("*.eml"))
        logger.info(f"Found {len(eml_files)} .eml files to process")

        for eml_path in eml_files:
            email_data = parse_eml_file(str(eml_path))
            if email_data and len(email_data.get("body", "")) > 10:
                emails.append(email_data)

        logger.info(f"Successfully parsed {len(emails)} emails from PST")

        # If we got very few emails, try folder parsing as fallback
        if len(emails) < 5:
            logger.warning(f"Only {len(emails)} emails found. Checking for other formats...")
            # Look for any other text files
            for txt_file in Path(extract_dir).rglob("*"):
                if txt_file.is_file() and txt_file.suffix not in ['.eml']:
                    try:
                        with open(txt_file, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                        if len(content) > 50:
                            parsed = parse_emails_from_blob(content)
                            emails.extend(parsed)
                    except Exception:
                        continue

        # Ensure extracted directory exists
        os.makedirs(settings.EXTRACTED_DIR, exist_ok=True)

        # Write to JSON
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(emails, f, indent=2, ensure_ascii=False)

        logger.info(f"Extraction complete for {upload_id}. Saved {len(emails)} emails to {output_file}")

        # Trigger Indexing
        from services.index.service import index_messages
        index_messages(upload_id)

    except subprocess.TimeoutExpired:
        logger.error("readpst timed out after 1 hour")
    except FileNotFoundError:
        logger.error("readpst not found. Install pst-utils package.")
        # Fall back to Tika
        process_pst_with_tika(file_path, upload_id, output_file)
    except Exception as e:
        logger.exception(f"Error processing file {file_path}: {e}")
    finally:
        # Clean up temp directory
        try:
            shutil.rmtree(extract_dir)
        except Exception:
            pass


def process_pst_with_tika(file_path: str, upload_id: str, output_file: str):
    """Fallback to Tika for PST parsing (less reliable)."""
    try:
        from tika import parser
        logger.info("Using Tika fallback for PST parsing...")
        parsed = parser.from_file(
            file_path,
            serverEndpoint=settings.TIKA_SERVER_URL,
            requestOptions={'timeout': 3600}
        )

        content = parsed.get("content", "")
        logger.info(f"Tika returned {len(content)} characters")

        emails = parse_emails_from_blob(content)
        logger.info(f"Parsed {len(emails)} emails via Tika")

        os.makedirs(settings.EXTRACTED_DIR, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(emails, f, indent=2, ensure_ascii=False)

        from services.index.service import index_messages
        index_messages(upload_id)
    except Exception as e:
        logger.exception(f"Tika fallback failed: {e}")


async def handle_upload(file, background_tasks: BackgroundTasks):
    """Handle PST file upload."""
    # Generate a unique ID based on file content hash for deduplication
    file_content = file.file.read()
    file_hash = hashlib.md5(file_content).hexdigest()[:16]
    file.file.seek(0)  # Reset file pointer
    
    # Check if this exact file was already uploaded
    existing_uploads = get_existing_upload_ids()
    for existing_id in existing_uploads:
        if file_hash in existing_id:
            logger.info(f"File already uploaded with ID: {existing_id}")
            return {
                "upload_id": existing_id,
                "status": "already_processed",
                "message": "This file was already uploaded and processed. Using existing data."
            }
    
    upload_id = f"{file_hash}-{str(uuid.uuid4())[:8]}"
    filename = f"{upload_id}.pst"
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
        
    logger.info(f"File saved to {file_path}")
    
    # Run processing in background
    background_tasks.add_task(process_pst_file, file_path, upload_id)
    
    return {
        "upload_id": upload_id,
        "status": "processing",
        "message": "File uploaded. Processing started in background."
    }


async def get_upload_status(upload_id: str) -> dict:
    """Get the status of an upload."""
    output_file = os.path.join(settings.EXTRACTED_DIR, f"{upload_id}.json")
    
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            emails = json.load(f)
        return {
            "upload_id": upload_id,
            "status": "completed",
            "email_count": len(emails),
            "message": f"Successfully extracted {len(emails)} emails"
        }
    
    # Check if PST file exists (still processing)
    pst_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}.pst")
    if os.path.exists(pst_path):
        return {
            "upload_id": upload_id,
            "status": "processing",
            "message": "File is being processed"
        }
    
    return {
        "upload_id": upload_id,
        "status": "not_found",
        "message": "Upload not found"
    }
