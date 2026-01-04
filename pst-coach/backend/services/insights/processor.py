import json
import os
from typing import List, Dict
from loguru import logger
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from core.config import settings

# Define the schema for insights
# We want structured output
INSIGHTS_PROMPT = """
You are an expert executive coach and behavioral analyst. 
Your task is to analyze the following email communication history of a user and provide deep, actionable insights.
Focus on "Self-reflection", "Communication patterns", "Workload boundaries", and "Tone".

DO NOT provide medical or psychological diagnoses. Use coaching language (e.g., "patterns suggest", "tendency to").

Here is the email data (metadata + body snippets):
{email_data}

Generate a JSON response with the following keys:
1. "summary": A high-level executive summary of the user's communication style (approx 3-4 sentences).
2. "behavioral_patterns": List of observed behaviors (e.g., "High responsiveness late at night", "Apologetic language").
3. "coaching_tips": List of actionable advice to improve communication or work-life balance.
4. "mood_trends": Description of the general tone (e.g., "Urgent", "Calm", "Frustrated") and any noticeable shifts.
5. "strengths": What the user does well.
6. "areas_for_improvement": Specific things to work on.

JSON Output:
"""

def generate_insights(upload_id: str):
    """
    Generate insights using Claude 3.5 Sonnet.
    """
    logger.info(f"Starting insights generation for {upload_id}")
    
    input_file = os.path.join(settings.EXTRACTED_DIR, f"{upload_id}.json")
    if not os.path.exists(input_file):
        logger.error(f"File not found: {input_file}")
        return

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Preprocessing:
        # We can't fit infinite emails. Let's take the last 100 sent items or a mix.
        # For MVP, let's take a representative sample of Sent items (to analyze the USER'S style) regarding "Self-reflection".
        # If we analyze *received* emails, we analyze others. The user wants "insights about *myself*".
        # So filtering for "Sent" items if possible is key. 
        # But we don't strictly know which is "Sent" without user identity.
        # Heuristic: "From" field matches most frequent sender? Or just analyze all to see interaction patterns?
        # Let's analyze a mix but try to identify the user.
        
        # Simple heuristic: Identify most frequent sender
        import collections
        senders = [d.get("from") for d in data if d.get("from")]
        if senders:
            most_common_sender = collections.Counter(senders).most_common(1)[0][0]
            logger.info(f"Assuming user identity is: {most_common_sender}")
            
            # Filter for emails FROM the user to analyze THEIR output
            user_emails = [d for d in data if d.get("from") == most_common_sender]
            # Also keep some context of what they are replying to? 
            # For now, just analyze their output for "Psychological assessment".
            
            analysis_set = user_emails[:50] # Take last 50 emails for speed/cost in MVP
        else:
            analysis_set = data[:50]

        # Prepare text blob
        email_text = ""
        for email in analysis_set:
            email_text += f"---\nDate: {email.get('date')}\nSubject: {email.get('subject')}\nBody: {email.get('body')[:500]}\n"

        if not email_text:
            logger.warning("No email text found to analyze.")
            return

        # Call Claude
        logger.info("Calling Claude for insights...")
        llm = ChatAnthropic(
            model=settings.LLM_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=0.2
        )
        
        chain = ChatPromptTemplate.from_template(INSIGHTS_PROMPT) | llm | JsonOutputParser()
        
        result = chain.invoke({"email_data": email_text})
        
        # Save result
        output_file = os.path.join(settings.DATA_DIR, "insights", f"{upload_id}_insights.json")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
            
        logger.info(f"Insights generated and saved to {output_file}")

    except Exception as e:
        logger.exception(f"Error generating insights: {e}")
