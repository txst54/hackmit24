from controls.docvision import (
    encode_images,
    create_content,
    get_openai_response,
    get_bounding_boxes,
    match_boxes,
    place_answers_on_image,
)


def fill_pdf_via_image(pdf_name: str, data: Dict[str, str]) -> str:
    """Fills out a pdf composing of images with the given data in the form of a dictionary of field names and values"""
    print("DATAAAAAAAAA", data)
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
