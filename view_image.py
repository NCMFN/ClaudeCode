from PIL import Image

def summarize_image(path):
    img = Image.open(path)
    print(f"Format: {img.format}, Size: {img.size}, Mode: {img.mode}")

summarize_image("/tmp/file_attachments/image.png")
