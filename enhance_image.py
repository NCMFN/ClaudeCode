import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance, ImageFilter

# 1. Apply the global Matplotlib settings before processing
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300
})

def enhance_pipeline_diagram(image_path, output_path):
    """
    Enhances a pipeline diagram image to improve readability, sharpness, and contrast.

    Args:
        image_path (str): Path to the original input image.
        output_path (str): Path to save the enhanced image.
    """
    # 2. Load the uploaded image
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: Could not find image at {image_path}")
        return

    # Convert to RGB if it has an alpha channel to ensure proper filtering and saving
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        img = img.convert('RGBA')
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3]) # 3 is the alpha channel
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # 3. Apply image enhancement techniques

    # Increase DPI / resolution (scale by 2 for sharper text when filtered)
    new_size = (img.width * 2, img.height * 2)
    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)

    # Contrast adjustment to differentiate boxes and arrows from the background
    contrast_enhancer = ImageEnhance.Contrast(img_resized)
    img_contrast = contrast_enhancer.enhance(1.8) # Increase contrast by 80%

    # Sharpening filters to make text edges crisper
    sharpness_enhancer = ImageEnhance.Sharpness(img_contrast)
    img_sharp = sharpness_enhancer.enhance(2.5) # Increase sharpness significantly

    # Optional: Enhance color slightly to make colored boxes (e.g., purple/blue) pop
    color_enhancer = ImageEnhance.Color(img_sharp)
    img_color = color_enhancer.enhance(1.2)

    # Optional: Noise reduction and unsharp mask for further edge enhancement
    img_final = img_color.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

    # 4. Display the improved image inline using Matplotlib
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.imshow(img_final)
    ax.set_title("Enhanced Architecture Diagram", pad=15)
    ax.axis('off') # Hide axes for cleaner display
    plt.tight_layout()
    plt.show() # Display inline

    # 5. Save the enhanced version to disk
    # We use PIL's save method for direct image saving without Matplotlib borders,
    # and specify dpi to match the requirements.
    img_final.save(output_path, dpi=(300, 300))
    print(f"Saved enhanced image to {output_path}")

if __name__ == "__main__":
    input_image = "AER1.png"
    output_image = "enhanced_architecture.png"
    enhance_pipeline_diagram(input_image, output_image)
