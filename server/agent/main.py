import PIL
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import ReActAgent
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
from typing import List, Dict, Any, Annotated
import difflib
import subprocess
from get_emails import run_email
from email_priority import prioritize_emails_to_todoist
from controls.codeagents import (
    read_pull,
    post_comment_to_pr,
    find_commit_sha_by_code_segment,
)
from controls.docvision import (
    encode_images,
    create_content,
    get_openai_response,
    get_bounding_boxes,
    match_boxes,
    place_answers_on_image,
)
from cal import schedule_meeting
import llama_index.core
import os

PHOENIX_API_KEY = "a77688ad1327d14a0b3:9f469be"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"api_key={PHOENIX_API_KEY}"
llama_index.core.set_global_handler(
    "arize_phoenix", endpoint="https://llamatrace.com/v1/traces"
)

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

    for field in fields:
        try:
            writer.update_page_form_field_values(
                writer.pages[0],
                {field: data[field]},
                auto_regenerate=False,
            )
        except Exception:
            continue

    with open("fillable.pdf", "wb") as output_file:
        writer.write(output_file)
    return "pdf filled and saved to fillable.pdf"


def open_pdf(pdf_name: str) -> bool:
    """opens pdf file using system default pdf reader"""
    # subprocess.run(["open", pdf_name], shell=True)
    os.system(f"open {pdf_name}")
    return True


def add_todo(todo: str) -> str:
    """add todo to a global variable"""
    todos.append(todo)
    return f"todo added to todos: {todo}"


def images_to_pdf(input_data: List[Any], output_path: str) -> None:
    """Convert an array of images into a pdf and writes it"""
    # Convert all images to RGB mode (PDF requires RGB mode)
    rgb_images = [img.convert("RGB") for img in input_data]
    print(input_data)
    # Save the first image and append the rest as additional pages
    rgb_images[0].save(
        output_path,
        save_all=True,
        append_images=rgb_images[1:],
        resolution=100.0,
        quality=95,
        optimize=True,
    )


def load_pdf_to_image(pdf_name: str) -> Dict[str, Any]:
    """Loads pdf to an array of images"""
    images = convert_from_path(pdf_name)
    encoded_images = encode_images(images)

    return {"images": images, "encoded": encoded_images}


def get_fields_from_image(pdf_name: str) -> List[str]:
    """returns fields needed to fill out a pdf file if the pdf consists of images only"""
    img_obj = load_pdf_to_image(pdf_name)
    content = create_content(
        img_obj["encoded"],
        "List all of the form field names as written on the document. Output it "
        "in a comma separated list. Don't bullet or enumerate.",
    )
    response = get_openai_response(content)
    return response.split(", ")


def fill_pdf_via_image(pdf_name: str, data: Dict[str, str]) -> str:
    """Fills out a pdf composing of images with the given data in the form of a dictionary of field names and values"""
    img_obj = load_pdf_to_image(pdf_name)
    images = img_obj["images"]
    fields = get_fields_from_image(pdf_name)
    page_list = []
    for page in images:
        bounding_boxes = get_bounding_boxes(page)
        prompts, coords = match_boxes(bounding_boxes, fields)

        answers = []
        try:
            for p in prompts:
                matched = False
                for data_key in data.keys():
                    r = difflib.SequenceMatcher(None, p, data_key).ratio()
                    if r >= 0.7:
                        answers.append(data[data_key])
                        matched = True
                        break
                if not matched:
                    answers.append("")
        except Exception:
            continue

        new_page = place_answers_on_image(page, answers, coords)
        print("Appending...")
        page_list.append(new_page)
    images_to_pdf(page_list, "non_fillable.pdf")
    return "success, written to non_fillable.pdf"


get_fields_function = FunctionTool.from_defaults(fn=get_fields)
get_data_function = FunctionTool.from_defaults(fn=get_data)
fill_pdf_function = FunctionTool.from_defaults(fn=fill_pdf)
open_pdf_function = FunctionTool.from_defaults(fn=open_pdf)
add_todo_function = FunctionTool.from_defaults(fn=add_todo)
images_to_pdf_function = FunctionTool.from_defaults(fn=images_to_pdf)
get_fields_from_image_function = FunctionTool.from_defaults(fn=get_fields_from_image)
fill_pdf_via_image_function = FunctionTool.from_defaults(fn=fill_pdf_via_image)
read_pull_function = FunctionTool.from_defaults(fn=read_pull)
find_commit_sha_by_code_segment_function = FunctionTool.from_defaults(
    fn=find_commit_sha_by_code_segment
)
post_comment_to_pr_function = FunctionTool.from_defaults(fn=post_comment_to_pr)
prioritize_emails_to_todoist_function = FunctionTool.from_defaults(
    fn=prioritize_emails_to_todoist
)
schedule_meeting_function = FunctionTool.from_defaults(fn=schedule_meeting)

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
        images_to_pdf_function,
        get_fields_from_image_function,
        fill_pdf_via_image_function,
        read_pull_function,
        post_comment_to_pr_function,
        find_commit_sha_by_code_segment_function,
        schedule_meeting_function,
    ],
    llm=llm,
    verbose=True,
    max_iterations=10,
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
            1. Download the attachment, fill out the pdf with appropriate function (if there's not fields use image reltated functions).Be careful some forms have the year as 4 fields instead of 1. put each digit in each field.
            2. Add the email as a dictionary to the todo list. dictionary should have the following keys: subject, sender, snippet, due_date. include all the data from original email. summarize the body. sender should have name and email.
            3. Schedule a meeting with the sender of the email if the email has timeslots instead of todo tasks.
            4. Review the pull-request and suggest any changes to make before merging. Write code suggestions to github as a comment.Make sure to open the root url of the pull request.
            
        """
        )
    # prioritize_emails_to_todoist(todos)
    if len(todos) != 0:
        prioritize_emails_to_todoist(todos)
    # find_commit_sha_by_code_segment("Texas-Capital-Collective", "tcc-golf", "11", "-    <div class=\"w-10/12 lg:pb-16\">")
    # post_comment_to_pr("https://github.com/Texas-Capital-Collective/tcc-golf/pull/11", "Testing new TCC Dev Tool :)")
    # read_pull("https://github.com/Texas-Capital-Collective/tcc-golf/pull/11")
    # fill_pdf_via_image("./downloads/hard-pdf.pdf", data)
