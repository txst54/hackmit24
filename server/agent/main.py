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
from controls.docvision import (
    encode_images,
    create_content,
    get_openai_response,
    get_bounding_boxes,
    match_boxes,
    place_answers_on_image,
)
from pydantic import FilePath, field_validator, BeforeValidator
from PIL import Image
from pydantic import BaseModel

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
    print("Data: ", data)
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
    images_to_pdf(page_list, "output.pdf")
    return "success, written to output.pdf"


get_fields_function = FunctionTool.from_defaults(fn=get_fields)
get_data_function = FunctionTool.from_defaults(fn=get_data)
fill_pdf_function = FunctionTool.from_defaults(fn=fill_pdf)
open_pdf_function = FunctionTool.from_defaults(fn=open_pdf)
add_todo_function = FunctionTool.from_defaults(fn=add_todo)
images_to_pdf_function = FunctionTool.from_defaults(fn=images_to_pdf)
load_pdf_to_image_function = FunctionTool.from_defaults(fn=load_pdf_to_image)
get_fields_from_image_function = FunctionTool.from_defaults(fn=get_fields_from_image)
fill_pdf_via_image_function = FunctionTool.from_defaults(fn=fill_pdf_via_image)
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
        images_to_pdf_function,
        load_pdf_to_image_function,
        get_fields_from_image_function,
        fill_pdf_via_image_function,
    ],
    llm=llm,
    verbose=True,
)

if __name__ == "__main__":
    # emails = run_email()
    # # print([email["attachments"] for email in emails])
    # for email in emails:
    #     agent.chat(
    #         # "create a dictionary of fields and values based on pdf file called easy-pdf.pdf and given data. use that dictionary to fill out the pdf file"
    #         # "fill out the pdf called easy-pdf.pdf and open the edited version. Be careful some forms have the year as 4 fields instead of 1. put each digit in each field."
    #         f"""
    #         email body: {email['content']}
    #         email attachements: {email['attachments']}
    #         email sender: {email['sender']}
    #         email subject: {email['subject']}
    #         Based on the email above, do one of the following tasks:
    #         1. Download the attachemnt, fill out the pdf with appropriate function (if there's not fields use image reltated functions), and open the edited version.Be careful some forms have the year as 4 fields instead of 1. put each digit in each field.
    #         2. Add the email as a dictionary to the todo list. dictionary should have the following keys: subject, sender, snippet, due_date. include all the data from original email. summarize the body.
    #     """
    #     )
    # prioritize_emails_to_todoist(todos)
    data = {
        "IDENTIFICATION NUMBER": "1HGCM82633A123456",
        "YEAR MODEL": "2015",
        "MAKE": "Toyota",
        "LICENSE PLATE#/#": "ABC1234",
        "MOTORCYCLE ENGINE#": "",
        "PRINT SELLER'S NAME(S)": "John Doe",
        "MD": "09",
        "DAY": "14",
        "YR": "2024",
        "SELLING PRICE": "$15,000",
        "GIFT VALUE": "",
        "PRINT NAME": "John Doe",
        "SIGNATURE": "John Doe",
        "DATE": "09/14/2024",
        "DL. or DEALER#": "D1234567",
        "MAILING ADDRESS": "123 Main St",
        "CITY": "San Francisco",
        "STATE": "CA",
        "ZIP": "94105",
        "DAYTIME PHONE#": "(310) 555-1234",
        "BUYER PRINT NAME": "Jane Smith",
    }
    fill_pdf_via_image("./downloads/hard-pdf.pdf", data)
