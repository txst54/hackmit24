import requests
from dotenv import dotenv_values

config = dotenv_values(".env")

def create_issue(repo_owner, repo_name, issue_title, issue_body):
    # Replace these variables with your details
    GITHUB_TOKEN = config["GITHUB"]
    REPO_OWNER = repo_owner
    REPO_NAME = repo_name
    ISSUE_TITLE = issue_title
    ISSUE_BODY = issue_body

    # GitHub API URL to create an issue
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'

    # Headers with authentication
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Payload with issue details
    payload = {
        'title': ISSUE_TITLE,
        'body': ISSUE_BODY
    }

    # Make the request to create the issue
    response = requests.post(url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 201:
        print('Issue created successfully:', response.json())
    else:
        print('Failed to create issue:', response.status_code, response.json())