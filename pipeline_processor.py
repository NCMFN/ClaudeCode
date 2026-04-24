import cv2
import numpy as np
import matplotlib.pyplot as plt

def main():
    # Load image
    image_path = "AER10.png"
    img = cv2.imread(image_path)

    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return

    # Auto-detect the pipeline using contours (fully automatic cropping)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # Dilate to connect components
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
    dilated = cv2.dilate(thresh, kernel, iterations=1)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    center_x = img.shape[1] // 2
    pipeline_boxes = []

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        # Check the center of the bounding box
        box_cx = x + w // 2
        # If the box center is within 20% of the image center, it's likely part of the central pipeline
        if abs(box_cx - center_x) < img.shape[1] * 0.2:
            pipeline_boxes.append((x, y, w, h))

    if pipeline_boxes:
        min_x = min([b[0] for b in pipeline_boxes])
        min_y = min([b[1] for b in pipeline_boxes])
        max_x = max([b[0] + b[2] for b in pipeline_boxes])
        max_y = max([b[1] + b[3] for b in pipeline_boxes])

        pad = 30
        min_x = max(0, min_x - pad)
        min_y = max(0, min_y - pad)
        max_x = min(img.shape[1], max_x + pad)
        max_y = min(img.shape[0], max_y + pad)

        crop = img[min_y:max_y, min_x:max_x]
    else:
        # Fallback to manual crop if auto-detect fails
        h, w, _ = img.shape
        crop = img[int(h*0.05):int(h*0.95), int(w*0.25):int(w*0.75)]

    # Rotate 90° counterclockwise
    rotated = cv2.rotate(crop, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # Enhance clarity (sharpness + contrast)
    lab = cv2.cvtColor(rotated, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l_clahe = clahe.apply(l)

    enhanced_lab = cv2.merge((l_clahe, a, b))
    enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])

    sharpened = cv2.filter2D(enhanced, -1, kernel)

    output_path = "horizontal_pipeline.png"
    cv2.imwrite(output_path, sharpened)

    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    main()
