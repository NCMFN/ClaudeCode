from PIL import Image
def extract_colors(image_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    width, height = img.size

    colors = set()
    for x in range(0, width, 10):
        for y in range(0, height, 10):
            r, g, b = img.getpixel((x, y))
            if not (r > 240 and g > 240 and b > 240) and not (r < 15 and g < 15 and b < 15):
                colors.add((r, g, b))

    # simple color clustering or sampling
    print("Sample colors found (RGB):")
    for c in list(colors)[:20]:
        print(c)

extract_colors("/tmp/file_attachments/image.png")
