def extract_text(tag, class_name=None):
    # :: Extract and return text from a tag if it exists.
    element = tag.find(class_name=class_name) if class_name else tag
    return element.text.strip() if element else None
