"""
PST Data Extraction and Quality Analysis Script

This script:
1. Extracts emails from PST file using Apache Tika
2. Analyzes data quality (checking for specific names like Dina Cartagena)
3. Saves extracted data for indexing
"""

import os
import sys
import json
import hashlib
import re
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from tika import parser
from core.config import settings

# Configure logger
logger.add("logs/extraction.log", rotation="10 MB")


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
    text = re.sub(r"_{10,}", "", text)  # Remove separator lines
    return text.strip()


def parse_emails_from_blob(content: str) -> list:
    """
    Parse individual emails from a large text blob.
    Improved parsing to capture more email metadata.
    """
    emails = []
    
    if not content:
        return emails
    
    # Split by "From:" headers which typically start emails
    # Use a more flexible pattern to catch various formats
    from_splits = re.split(r'\n(?=From:\s*[^\n]+)', content)
    
    logger.info(f"Found {len(from_splits)} potential email sections")
    
    for i, section in enumerate(from_splits):
        if len(section.strip()) < 30:  # Skip very short sections
            continue
            
        # Extract metadata from the section
        from_match = re.search(r'From:\s*(.+?)(?:\n|$)', section, re.IGNORECASE)
        sent_match = re.search(r'Sent:\s*(.+?)(?:\n|$)', section, re.IGNORECASE)
        date_match = re.search(r'Date:\s*(.+?)(?:\n|$)', section, re.IGNORECASE)
        to_match = re.search(r'To:\s*(.+?)(?:\n|$)', section, re.IGNORECASE)
        cc_match = re.search(r'Cc:\s*(.+?)(?:\n|$)', section, re.IGNORECASE)
        subject_match = re.search(r'Subject:\s*(.+?)(?:\n|$)', section, re.IGNORECASE)
        
        # Get the body (everything after the headers)
        body = section
        # Remove header lines from body
        for pattern in [r'^From:.*?\n', r'^Sent:.*?\n', r'^Date:.*?\n', 
                       r'^To:.*?\n', r'^Cc:.*?\n', r'^Subject:.*?\n',
                       r'^Received:.*?\n', r'^Message-ID:.*?\n']:
            body = re.sub(pattern, '', body, flags=re.IGNORECASE | re.MULTILINE)
        body = clean_body(body)
        
        if len(body) < 10:  # Skip emails with very short bodies
            continue
        
        sender = from_match.group(1).strip() if from_match else "Unknown Sender"
        subject = subject_match.group(1).strip() if subject_match else f"Email {i+1}"
        recipient = to_match.group(1).strip() if to_match else ""
        cc = cc_match.group(1).strip() if cc_match else ""
        date_str = (sent_match.group(1) if sent_match else 
                   date_match.group(1) if date_match else 
                   str(datetime.now())).strip()
        
        email_data = {
            "subject": subject,
            "from": sender,
            "to": recipient,
            "cc": cc,
            "date": date_str,
            "body": body,
            "email_id": hashlib.md5(f"{sender}{subject}{body[:100]}".encode()).hexdigest()
        }
        emails.append(email_data)
    
    # If no emails found with headers, try splitting by common separators
    if len(emails) == 0:
        logger.warning("No emails found with standard headers, trying separators...")
        separator_splits = re.split(r'\n-{5,}.*?-{5,}\n', content)
        
        for i, section in enumerate(separator_splits):
            section = clean_body(section)
            if len(section) < 50:
                continue
                
            emails.append({
                "subject": f"Message {i+1}",
                "from": "PST Import",
                "to": "",
                "cc": "",
                "date": str(datetime.now()),
                "body": section,
                "email_id": hashlib.md5(section[:200].encode()).hexdigest()
            })
    
    return emails


def extract_pst_with_tika(pst_path: str) -> tuple[str, dict]:
    """
    Extract PST content using Apache Tika.
    Returns tuple of (content, metadata).
    """
    # Use localhost for local execution (outside Docker network)
    tika_url = "http://localhost:9998"
    logger.info(f"Extracting PST using Tika: {pst_path}")
    logger.info(f"Tika server URL: {tika_url}")
    
    try:
        parsed = parser.from_file(
            pst_path,
            serverEndpoint=tika_url,
            requestOptions={'timeout': 3600}
        )
        
        content = parsed.get("content", "")
        metadata = parsed.get("metadata", {})
        
        logger.info(f"Tika extracted {len(content)} characters")
        logger.info(f"Metadata keys: {list(metadata.keys())[:10]}")
        
        return content, metadata
        
    except Exception as e:
        logger.error(f"Tika extraction failed: {e}")
        raise


def analyze_data_quality(emails: list, search_names: list = None) -> dict:
    """
    Analyze the quality of extracted email data.
    Search for specific names if provided.
    """
    if search_names is None:
        search_names = ["Dina", "Cartagena", "Dina Cartagena"]
    
    analysis = {
        "total_emails": len(emails),
        "emails_with_sender": 0,
        "emails_with_recipient": 0,
        "emails_with_subject": 0,
        "emails_with_date": 0,
        "avg_body_length": 0,
        "unique_senders": set(),
        "unique_recipients": set(),
        "name_search_results": {name: [] for name in search_names}
    }
    
    total_body_length = 0
    
    for email in emails:
        # Count filled fields
        if email.get("from") and email["from"] != "Unknown Sender":
            analysis["emails_with_sender"] += 1
            analysis["unique_senders"].add(email["from"])
            
        if email.get("to"):
            analysis["emails_with_recipient"] += 1
            # Handle multiple recipients
            for recipient in email["to"].split(";"):
                analysis["unique_recipients"].add(recipient.strip())
                
        if email.get("subject") and not email["subject"].startswith("Email "):
            analysis["emails_with_subject"] += 1
            
        if email.get("date") and email["date"] != str(datetime.now()):
            analysis["emails_with_date"] += 1
            
        total_body_length += len(email.get("body", ""))
        
        # Search for specific names
        email_text = f"{email.get('from', '')} {email.get('to', '')} {email.get('subject', '')} {email.get('body', '')}"
        for name in search_names:
            if name.lower() in email_text.lower():
                analysis["name_search_results"][name].append({
                    "from": email.get("from", "")[:50],
                    "to": email.get("to", "")[:50],
                    "subject": email.get("subject", "")[:50],
                    "date": email.get("date", "")[:30],
                    "body_preview": email.get("body", "")[:100]
                })
    
    # Calculate averages
    if len(emails) > 0:
        analysis["avg_body_length"] = total_body_length // len(emails)
    
    # Convert sets to lists for JSON serialization
    analysis["unique_senders"] = sorted(list(analysis["unique_senders"]))[:50]
    analysis["unique_recipients"] = sorted(list(analysis["unique_recipients"]))[:50]
    
    return analysis


def print_analysis_report(analysis: dict):
    """Print a human-readable analysis report."""
    print("\n" + "="*60)
    print("PST DATA QUALITY ANALYSIS REPORT")
    print("="*60)
    
    print(f"\n📧 Total Emails Extracted: {analysis['total_emails']}")
    print(f"   - With Sender: {analysis['emails_with_sender']} ({100*analysis['emails_with_sender']//max(1,analysis['total_emails'])}%)")
    print(f"   - With Recipient: {analysis['emails_with_recipient']} ({100*analysis['emails_with_recipient']//max(1,analysis['total_emails'])}%)")
    print(f"   - With Subject: {analysis['emails_with_subject']} ({100*analysis['emails_with_subject']//max(1,analysis['total_emails'])}%)")
    print(f"   - With Date: {analysis['emails_with_date']} ({100*analysis['emails_with_date']//max(1,analysis['total_emails'])}%)")
    print(f"   - Average Body Length: {analysis['avg_body_length']} chars")
    
    print(f"\n👥 Unique Senders ({len(analysis['unique_senders'])}):")
    for sender in analysis['unique_senders'][:20]:
        print(f"   - {sender}")
    if len(analysis['unique_senders']) > 20:
        print(f"   ... and {len(analysis['unique_senders']) - 20} more")
        
    print(f"\n📬 Unique Recipients ({len(analysis['unique_recipients'])}):")
    for recipient in analysis['unique_recipients'][:20]:
        print(f"   - {recipient}")
    if len(analysis['unique_recipients']) > 20:
        print(f"   ... and {len(analysis['unique_recipients']) - 20} more")
    
    print("\n🔍 NAME SEARCH RESULTS:")
    for name, results in analysis['name_search_results'].items():
        print(f"\n   '{name}': {len(results)} matches")
        for r in results[:5]:
            print(f"      From: {r['from']}")
            print(f"      To: {r['to']}")
            print(f"      Subject: {r['subject']}")
            print(f"      Date: {r['date']}")
            print(f"      Preview: {r['body_preview'][:60]}...")
            print("      ---")
    
    print("\n" + "="*60)


def main():
    """Main extraction and analysis pipeline."""
    
    # PST file path
    pst_path = r"c:\CodeJaai\RAG-personal\PST\iaurang@clemson.edu.pst"
    
    if not os.path.exists(pst_path):
        logger.error(f"PST file not found: {pst_path}")
        print(f"❌ PST file not found: {pst_path}")
        return
    
    file_size_mb = os.path.getsize(pst_path) / (1024 * 1024)
    print(f"📁 PST file found: {pst_path}")
    print(f"   Size: {file_size_mb:.2f} MB")
    
    # Extract using Tika
    print("\n🔄 Extracting emails using Apache Tika...")
    try:
        content, metadata = extract_pst_with_tika(pst_path)
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        print("\n⚠️ Make sure Tika is running: docker-compose up -d tika")
        return
    
    if not content:
        print("❌ No content extracted from PST file")
        return
        
    print(f"✅ Extracted {len(content)} characters of content")
    
    # Parse emails from content
    print("\n🔄 Parsing individual emails...")
    emails = parse_emails_from_blob(content)
    print(f"✅ Parsed {len(emails)} individual emails")
    
    # Analyze data quality
    print("\n🔄 Analyzing data quality...")
    search_names = ["Dina", "Cartagena", "Dina Cartagena", "Freeman", "Dr. Freeman"]
    analysis = analyze_data_quality(emails, search_names)
    
    # Print report
    print_analysis_report(analysis)
    
    # Save extracted emails to JSON
    output_dir = settings.EXTRACTED_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate upload_id from file hash
    with open(pst_path, 'rb') as f:
        file_hash = hashlib.md5(f.read(1024*1024)).hexdigest()[:16]  # Hash first 1MB
    upload_id = f"{file_hash}-manual"
    
    output_file = os.path.join(output_dir, f"{upload_id}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(emails, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved {len(emails)} emails to: {output_file}")
    print(f"   Upload ID: {upload_id}")
    
    # Save analysis report
    analysis_file = os.path.join(output_dir, f"{upload_id}_analysis.json")
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
    print(f"📊 Saved analysis to: {analysis_file}")
    
    return upload_id, emails, analysis


if __name__ == "__main__":
    main()
