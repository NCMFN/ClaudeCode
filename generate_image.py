from PIL import Image, ImageDraw, ImageFont

def create_invitation():
    try:
        # Load the background image
        img = Image.open('/tmp/file_attachments/lucy2.jpeg')
        draw = ImageDraw.Draw(img)

        # Define image dimensions to calculate centers
        width, height = img.size
        center_x = width / 2

        # Try to load a nice font, fallback to default if not available
        try:
            # Arial or similar default
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 60)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 40)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 30)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Text color (Gold-ish)
        text_color = (212, 175, 55) # Hex #D4AF37

        # Text definitions and vertical positioning
        texts = [
            ("You're cordially invited to", font_small, height * 0.25),
            ("Florence Okotie", font_large, height * 0.35),
            ("50th Birthday", font_medium, height * 0.45),
            ("Date: Saturday, 20 June 2026", font_medium, height * 0.55),
            ("Time: 10:00 AM", font_medium, height * 0.60),
            ("Ceremony:", font_small, height * 0.70),
            ("St Cyprian Catholic Church, New Oko Oba", font_medium, height * 0.75),
            ("Reception:", font_small, height * 0.85),
            ("St. Florence Hall, Dasilva Estate", font_medium, height * 0.90)
        ]

        # Draw each line of text centered
        for text, font, y_pos in texts:
            # Get bounding box of text to calculate width for centering
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]

            # Draw text
            draw.text((center_x - (text_width / 2), y_pos), text, font=font, fill=text_color)

        # Save output
        output_path = '/app/final_invitation.jpeg'
        img.save(output_path)
        print(f"Successfully created image at: {output_path}")

    except Exception as e:
        print(f"Error creating image: {e}")

if __name__ == "__main__":
    create_invitation()
