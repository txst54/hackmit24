import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from dotenv import load_dotenv

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

load_dotenv()


def get_gmail_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("creds.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def get_email_content(service, user_id, msg_id):
    try:
        message = (
            service.users()
            .messages()
            .get(userId=user_id, id=msg_id, format="full")
            .execute()
        )
        headers = {
            header["name"]: header["value"] for header in message["payload"]["headers"]
        }

        parts = message["payload"].get("parts", [])
        body = ""
        for part in parts:
            if part["mimeType"] == "text/plain":
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                break

        attachments = []
        for part in parts:
            if "filename" in part and part["filename"]:
                attachment = {
                    "filename": part["filename"],
                    "mimeType": part["mimeType"],
                    "headers": part.get("headers", []),
                }

                # Download attachment
                if "body" in part and "attachmentId" in part["body"]:
                    att_id = part["body"]["attachmentId"]
                    att = (
                        service.users()
                        .messages()
                        .attachments()
                        .get(userId=user_id, messageId=msg_id, id=att_id)
                        .execute()
                    )
                    file_data = base64.urlsafe_b64decode(att["data"].encode("UTF-8"))

                    # Create a 'downloads' directory if it doesn't exist
                    if not os.path.exists("downloads"):
                        os.makedirs("downloads")

                    # Save the file
                    file_path = os.path.join("downloads", part["filename"])
                    with open(file_path, "wb") as f:
                        f.write(file_data)

                    # Store the local file path instead of the attachment link
                    attachment["local_path"] = file_path

                attachments.append(attachment)

        email_data = {
            "content": body,
            "attachments": attachments,
            # "id": message["id"],
            "sender": {
                "name": headers.get("From", "").split("<")[0].strip(),
                "email": headers.get("From", "").split("<")[-1].rstrip(">"),
            },
            # "recipients": headers.get("To", "").split(","),
            # "cc": headers.get("Cc", "").split(",") if "Cc" in headers else [],
            "subject": headers.get("Subject", ""),
            "snippet": message["snippet"],
            # "payload": {
            #     "partId": message["payload"].get("partId", ""),
            #     "mimeType": message["payload"]["mimeType"],
            #     "filename": message["payload"].get("filename", ""),
            #     "content": body,
            #     "headers": [f"{k}:{v}" for k, v in headers.items()],
            #     "parts": attachments,
            # },
        }
        return email_data
    except Exception as error:
        print(f"An error occurred: {error}")
        return None


def run_email():
    service = get_gmail_service()
    user_id = "me"

    labels = service.users().labels().list(userId=user_id).execute()
    label_id = next(
        (label["id"] for label in labels["labels"] if label["name"] == "interaction"),
        None,
    )

    if not label_id:
        print("Label interaction not found.")
        return []

    results = (
        service.users().messages().list(userId=user_id, labelIds=[label_id]).execute()
    )
    messages = results.get("messages", [])

    if not messages:
        print("No messages found.")
    else:
        print("Messages:")
        data = []
        for message in messages:
            email_data = get_email_content(service, user_id, message["id"])
            if email_data:
                data.append(email_data)
    return data


print(run_email())
