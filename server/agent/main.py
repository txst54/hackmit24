from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import ReActAgent
from pypdf import PdfReader, PdfWriter
from typing import List, Dict, Any
import subprocess
from get_emails import run_email
from email_priority import prioritize_emails_to_todoist
from controls import docvision

todos = []


def get_data() -> str:
    """returns the data needed to fill out a pdf file"""
    return """Vehicle/Vessel Description:
Identification Number: 1HGCM82633A123456
Year Model: 2015
Make: Toyota
License Plate or CF #: ABC1234
Motorcycle Engine #: (Leave blank if not a motorcycle)
Seller Information:
Seller's Name: John Doe
Date of Sale: 09/14/2024
Selling Price: $15,000
Gift Value: (Leave blank if not a gift)
Seller's Certification:
Seller's Name: John Doe
Signature: John Doe
Date: 09/14/2024
DL, ID, or Dealer #: D1234567 (if applicable)
Mailing Address:
City: Los Angeles
State: CA
Zip: 90001
Daytime Phone Number: (310) 555-1234
Buyer Information:
Buyer's Name: Jane Smith
Mailing Address:
City: San Francisco
State: CA
Zip: 94105
"""


def get_fields(pdf_name: str) -> List[str]:
    """returns fields needed to fill out a pdf file"""
    reader = PdfReader(pdf_name)
    fields = reader.get_fields()

    return list(fields)


def fill_pdf(pdf_name: str, data: Dict[str, str]) -> str:
    """Fills out a pdf file with the given data in the form of a dictionary of field names and values"""
    reader = PdfReader(pdf_name)
    writer = PdfWriter()

    # page = reader.pages[0]
    fields = reader.get_fields()

    writer.append(reader)

    print("DATA:", data)
    for field in fields:
        try:
            writer.update_page_form_field_values(
                writer.pages[0],
                {field: data[field]},
                auto_regenerate=False,
            )
        except Exception:
            continue

    with open("output.pdf", "wb") as output_file:
        writer.write(output_file)
    return "pdf filled and saved to output.pdf"


def open_pdf(pdf_name: str) -> str:
    """opens pdf file using system default pdf reader"""
    subprocess.run(["open", pdf_name])
    return "file opened"


def add_todo(todo: str) -> str:
    """add todo to a global variable"""
    todos.append(todo)
    return f"todo added to todos: {todo}"


get_fields_function = FunctionTool.from_defaults(fn=get_fields)
get_data_function = FunctionTool.from_defaults(fn=get_data)
fill_pdf_function = FunctionTool.from_defaults(fn=fill_pdf)
open_pdf_function = FunctionTool.from_defaults(fn=open_pdf)
add_todo_function = FunctionTool.from_defaults(fn=add_todo)
prioritize_emails_to_todoist_function = FunctionTool.from_defaults(
    fn=prioritize_emails_to_todoist
)

# initialize llm
llm = OpenAI(model="gpt-4o")

# initialize ReAct agent
agent = ReActAgent.from_tools(
    [
        get_fields_function,
        get_data_function,
        fill_pdf_function,
        open_pdf_function,
        add_todo_function,
        prioritize_emails_to_todoist_function,
    ],
    llm=llm,
    verbose=True,
)


if __name__ == "__main__":
    emails = run_email()
    # print([email["attachments"] for email in emails])
    for email in emails:
        agent.chat(
            # "create a dictionary of fields and values based on pdf file called easy-pdf.pdf and given data. use that dictionary to fill out the pdf file"
            # "fill out the pdf called easy-pdf.pdf and open the edited version. Be careful some forms have the year as 4 fields instead of 1. put each digit in each field."
            f"""
            email body: {email['content']}
            email attachements: {email['attachments']}
            email sender: {email['sender']}
            email subject: {email['subject']}
            Based on the email above, do one of the following tasks:
            1. Download the attachemnt, fill out the pdf, and open the edited version.Be careful some forms have the year as 4 fields instead of 1. put each digit in each field.
            2. Add action item to todo list and include time left to do the task if there's a deadline.
        """
        )
    print(todos)
