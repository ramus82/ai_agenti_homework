import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def decode_image(encoded_string, output_path):
    with open(output_path, "wb") as output_file:
        output_file.write(base64.b64decode(encoded_string)) 

TBD