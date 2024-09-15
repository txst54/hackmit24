import PIL
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import ReActAgent
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
from typing import List, Dict, Any
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
from pydantic import FilePath, field_validator
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


class PILImageField(Image.Image):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, Image.Image):
            raise ValueError("Must be a PIL Image")
        return v


class ImageToPdfInput(BaseModel):
    image_list: List[PILImageField]
    output_pdf_path: FilePath

    @field_validator("image_list")
    def check_image_list_not_empty(cls, v):
        if not v:
            raise ValueError("The image list cannot be empty")
        return v

    class Config:
        arbitrary_types_allowed = True


def images_to_pdf(input_data: ImageToPdfInput) -> None:
    """Convert an array of images into a pdf and writes it"""
    # Convert all images to RGB mode (PDF requires RGB mode)
    rgb_images = [img.convert("RGB") for img in input_data.image_list]

    # Save the first image and append the rest as additional pages
    rgb_images[0].save(
        input_data.output_pdf_path,
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

        new_page = place_answers_on_image(page, [data[p] for p in prompts], coords)
        page_list.append(new_page)
    images_to_pdf(page_list, "./output.pdf")
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
            2. Add the email as a dictionary to the todo list. keep original json structure.
        """
        )
    print(todos)
