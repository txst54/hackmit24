from typing import Dict, List, Any, Tuple

import PIL
from openai import OpenAI
from dotenv import dotenv_values
from pdf2image import convert_from_path
import base64
from io import BytesIO
from PIL import ImageDraw, ImageFont
from google.cloud import vision
import io

config = dotenv_values(".env")
client = OpenAI(api_key=config["OPENAI"])


def encode_images(images):
    base64_images = []
    for i, image in enumerate(images):
        # Save each image
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()

        # Encode bytes to base64
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        base64_images.append(img_base64)
    return base64_images


def create_content(base64_images, text):
    content = [
        {"type": "text", "text": text}
    ]
    for img in base64_images:
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img}"
                }
            }
        )
    return content


def get_openai_response(content):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content


def place_answers_on_image(image: PIL.Image, answers: List[str], coordinates: List[List[Tuple[int]]]):
    # Open the image
    draw = ImageDraw.Draw(image)
    img_width, img_height = image.size
    # Load a font
    try:
        font = ImageFont.truetype("./arial.ttf", 30)  # You may need to adjust the font path or size
    except IOError:
        print("Error loading font...")
        font = ImageFont.load_default()
    old_answer = ""
    # Place each answer at the specified coordinates
    for answer, coord in zip(answers, coordinates):
        if answer == old_answer:
            continue
        old_answer = answer
        x = coord[0][0]
        y = coord[0][1]
        draw.text((x, y), answer, fill="black", font=font)

    # Save the result
    return image


def match_boxes(boxes, fields):
    prompts = []
    coords = []
    to_skip = 0
    for box in boxes:
        if to_skip != 0:
            to_skip -= 1
            continue
        for field in fields:
            if box['text'].description in field and not len(box['text'].description) == 1:
                prompts.append(field)
                coords.append(box['box'])
                to_skip = len(field.split(" "))
                break
    return prompts, coords


def get_bounding_boxes(image):
    vision_client = vision.ImageAnnotatorClient(credentials=None,
                                                client_options={"api_key": config["GCLOUD"]})

    # Convert the PIL image to a byte stream
    image_byte_array = io.BytesIO()
    image.save(image_byte_array, format='JPEG')  # Ensure to use the right format
    image_byte_array = image_byte_array.getvalue()
    # Use Vision API to detect text
    image = vision.Image(content=image_byte_array)
    response = vision_client.text_detection(image=image)
    texts = response.text_annotations

    # Extract bounding boxes for words (ignore first entry as it contains the entire text block)
    bounding_boxes = []
    for text in texts[1:]:
        box = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
        bounding_boxes.append({'text': text, 'box': box})

    return bounding_boxes


def images_to_pdf(image_list: List[PIL.Image], output_pdf_path: str):
    if not image_list:
        raise ValueError("The image list cannot be empty")

    # Convert all images to RGB mode (PDF requires RGB mode)
    rgb_images = [img.convert('RGB') for img in image_list]

    # Save the first image and append the rest as additional pages
    rgb_images[0].save(
        output_pdf_path,
        save_all=True,
        append_images=rgb_images[1:],
        resolution=100.0,
        quality=95,
        optimize=True
    )


def load_pdf_to_image(pdf_name: str) -> Dict[str, Any]:
    images = convert_from_path(pdf_name)
    encoded_images = encode_images(images)

    return {'images': images, 'encoded': encoded_images}


def get_fields_from_image(pdf_name: str) -> List[str]:
    img_obj = load_pdf_to_image(pdf_name)
    content = create_content(img_obj['encoded'],
                             "List all of the form field names as written on the document. Output it "
                             "in a comma separated list. Don't bullet or enumerate.")
    response = get_openai_response(content)
    return response.split(", ")


def fill_pdf_via_image(pdf_name: str, data: Dict[str, str]) -> str:
    img_obj = load_pdf_to_image(pdf_name)
    images = img_obj['images']
    fields = get_fields_from_image(pdf_name)
    page_list = []
    for page in images:
        bounding_boxes = get_bounding_boxes(page)
        prompts, coords = match_boxes(bounding_boxes, fields)

        new_page = place_answers_on_image(page, [data[p] for p in prompts], coords)
        page_list.append(new_page)
    images_to_pdf(page_list, "./output.pdf")
    return "success, written to output.pdf"
