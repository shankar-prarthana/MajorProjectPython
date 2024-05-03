import os
import cv2
import numpy as np
import math
import pytesseract
from PIL import Image

# Path to Tesseract executable (change this path as per your installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# Function to perform text detection using pytesseract
def detect_text(image):
    # Convert image to PIL format (required by pytesseract)
    image_pil = Image.fromarray(image)

    # Perform OCR using pytesseract
    text = pytesseract.image_to_string(image_pil)

    return text.strip()


# Function to calculate distance between 2 points
def distanceCalculate(p1, p2):
    """p1 and p2 in format (x1,y1) and (x2,y2) tuples"""
    dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    return dis


# Function to perform image processing and text detection
def process_image(image_path, positive_folder, negative_folder):
    # Load the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Threshold the image to obtain only the black parts
    ret, thresholded_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Invert the image
    thresholded_image = 255 - thresholded_image

    # Do an erosion operation using cross structure kernel to remove parts that are not horizontal or vertical
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
    thresholded_image = cv2.erode(thresholded_image, kernel, iterations=1)

    # Use LineSegmentDetector in CV2 to find the line segments in the image
    lsd = cv2.createLineSegmentDetector(0)
    dlines = lsd.detect(thresholded_image)

    # Get the line segments in the image
    # Find the distance and angle of the found line segments.
    # Select the line segment if the distance is > 25 and angle between 0 to 5 for horizontal and 85 to 90 for vertical lines
    line_image = np.zeros_like(thresholded_image)
    for dline in dlines[0]:
        x0 = int(round(dline[0][0]))
        y0 = int(round(dline[0][1]))
        x1 = int(round(dline[0][2]))
        y1 = int(round(dline[0][3]))
        dis = distanceCalculate((x0, y0), (x1, y1))  # Calculate distance using the provided function
        angle_between = math.degrees(math.atan2(abs(y1 - y0), abs(x1 - x0)))
        if dis > 25 and (0 <= angle_between < 5 or 85 < angle_between <= 90):
            cv2.line(line_image, (x0, y0), (x1, y1), 255, 5, cv2.LINE_AA)

    # Dilate the line image to fill gaps in between
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
    line_image = cv2.dilate(line_image, kernel, iterations=1)

    # Find contour and the associated bounding box
    # The area of graph bounding boxes will be large compared to other small line contours, this is used to find the graphs
    graph_mask = np.zeros_like(thresholded_image)
    contours, _ = cv2.findContours(line_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    selected_bounding_rect = []
    for ctr in contours:
        bounding_rect = cv2.boundingRect(ctr)
        bounding_rect_area = bounding_rect[2] * bounding_rect[3]
        if bounding_rect_area > 15000:  # This can be adjusted according to your need.
            contour_image = cv2.rectangle(graph_mask, bounding_rect, 255, -1)

    # Get the graph from original image from the mask
    selected_image = cv2.bitwise_and(image, image, mask=graph_mask)

    # Perform text detection on the selected image
    detected_text = detect_text(image)

    # Determine the category based on detected text and save the image accordingly
    if "negative" in detected_text.lower():
        save_path = os.path.join(negative_folder, os.path.basename(image_path))
    elif "positive" in detected_text.lower():
        save_path = os.path.join(positive_folder, os.path.basename(image_path))
    else:
        # If neither positive nor negative text is detected, save to a separate folder (optional)
        save_path = os.path.join(r'./Images/output/other', os.path.basename(image_path))

    # Save the extracted graph image
    cv2.imwrite(save_path, selected_image)


# Directory containing images
input_directory = r'./Images/input'
# Output directories for positive and negative images
positive_output_directory = r'./Images/output/Positive'
negative_output_directory = r'./Images/output/Negative'

# Ensure output directories exist
os.makedirs(positive_output_directory, exist_ok=True)
os.makedirs(negative_output_directory, exist_ok=True)

# Process each image in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        image_path = os.path.join(input_directory, filename)
        image_path = image_path.replace('\\', '/')
        print(image_path)
        process_image(image_path, positive_output_directory, negative_output_directory)

print("Process complete")