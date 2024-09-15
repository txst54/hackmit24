import json
from typing import List
from todoist_api_python.api import TodoistAPI
from textblob import TextBlob
import spacy
from dotenv import load_dotenv
import os

load_dotenv()

# python -m spacy download en_core_web_sm

# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")


def prioritize_emails_to_todoist(emails: List[dict]) -> str:
    # Initialize Todoist client
    api = TodoistAPI(os.environ["TODOIST_API_TOKEN"])

    # Create a new project
    project = api.add_project(name="Prioritized Tasks")

    for email in emails:
        subject = email["subject"]
        snippet = email["snippet"]
        content = f"{subject}\n\n{snippet}"

        # Perform sentiment analysis
        blob = TextBlob(content)
        sentiment = blob.sentiment.polarity

        # Perform NER
        doc = nlp(content)
        entities = [ent.label_ for ent in doc.ents]

        # Determine priority based on sentiment, entities, and keywords
        priority = determine_priority(sentiment, entities, content)

        # Create a task with the email content
        task_content = f"[{email['sender']['name']}] {subject}"
        task_description = f"From: {email['sender']['email']}\n\n{snippet}"

        # Map our priority to Todoist priority (4 is highest, 1 is lowest)
        todoist_priority = 4 if priority == "high" else 3 if priority == "medium" else 2

        api.add_task(
            content=task_content,
            description=task_description,
            project_id=project.id,
            priority=todoist_priority,
        )

    return f"https://todoist.com/app/project/{project.id}"


def determine_priority(sentiment: float, entities: List[str], content: str) -> str:
    # Priority keywords
    high_priority_keywords = ["urgent", "important", "deadline", "asap"]
    medium_priority_keywords = ["meeting", "project", "report"]

    # Check for high priority indicators
    if any(keyword in content.lower() for keyword in high_priority_keywords):
        return "high"
    if sentiment < -0.3 or "ORG" in entities or "PERSON" in entities:
        return "high"

    # Check for medium priority indicators
    if any(keyword in content.lower() for keyword in medium_priority_keywords):
        return "medium"
    if -0.3 <= sentiment < 0.3:
        return "medium"

    # Default to low priority
    return "low"


# Example usage
emails_json = [
    {
        "subject": "Urgent meeting tomorrow",
        "snippet": "We have an important client meeting tomorrow at 10 AM. Please prepare the presentation.",
        "sender": {"name": "John Doe", "email": "john@example.com"},
    },
    {
        "subject": "Weekend plans",
        "snippet": "Hey, what are your plans for the weekend? Want to grab lunch?",
        "sender": {"name": "Jane Smith", "email": "jane@example.com"},
    },
]

todoist_project_url = prioritize_emails_to_todoist(emails_json)
print(f"Todoist project created: {todoist_project_url}")

def prioritize(emails: List[dict]):
    todoist_project_url = prioritize_emails_to_todoist(emails)
    print(f"Todoist project created: {todoist_project_url}")

