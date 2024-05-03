import os
import csv
import re
from PIL import Image, ImageEnhance
import pytesseract
from fuzzywuzzy import fuzz

# Define paths and image directory
path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
image_directory = r".\Images\input"

# Set the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = path_to_tesseract

# Define regex patterns
result_pattern = re.compile(r'^(Positive|Negative)', re.IGNORECASE)
# Updated parameter pattern to capture parameters with hyphens and possible typos
parameter_pattern = re.compile(r'([A-Z-]+)\s+([\d.@Qe]+)\s*(\S+)\s*\[([^]]+)\]', re.IGNORECASE)

# Function to preprocess text data
# Function to preprocess text data
# Function to preprocess text data
def preprocess_data(value):
    # Replace commas and hyphens in the middle with periods
    value = value.replace(',', '.')
    # Replace hyphens only if they are followed by a digit or space
    value = re.sub(r'-\s*(\d|\s)', '.', value)
    # Replace other special characters with appropriate values
    value = value.replace('@', '0').replace('Q@', '0').replace('Q', '0').replace('e', '0').replace('e@', '0')
    return value



# Function to process each image
def process_image(image_path, csv_writer):
    # Enhance OCR by preprocessing the image
    img = Image.open(image_path).convert("RGB")
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)  # Increase contrast for better text extraction
    img = img.convert("L")  # Convert to grayscale

    text = pytesseract.image_to_string(img)
    print(f"Extracted text from {image_path}:")
    # Initialize variables to store data
    result = ''
    parameters = {key: '' for key in
                  ['WBC', 'RBC', 'HGB', 'HCT', 'MCV', 'MCH', 'MCHC', 'PLT', 'RDW-SD', 'RDW-CV', 'PDW', 'MPV',
                   'P-LCR', 'PCT', 'NEUT', 'LYMPH', 'MONO', 'EO', 'BASO', 'IG']}

    # Process each line of extracted text
    for line in text.split('\n'):
        if line.strip():
            # Check if the line contains positive or negative data
            result_match = result_pattern.match(line)
            if result_match:
                result = result_match.group(1)
            else:
                data_match = parameter_pattern.match(line)
                if data_match:
                    parameter = data_match.group(1)
                    value = preprocess_data(data_match.group(2))  # Preprocess data
                    unit = data_match.group(3)
                    # Use fuzzy matching for parameter names
                    for param_key in parameters.keys():
                        if fuzz.partial_ratio(param_key.lower(), parameter.lower()) > 90:
                            parameters[param_key] = value + ' ' + unit

    # Write the data to CSV if a result is found
    if result:
        csv_writer.writerow([result] + [parameters[key] for key in parameters])

# Initialize CSV writer and write CSV header only once
with open('output.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(
        ['Result', 'WBC', 'RBC', 'HGB', 'HCT', 'MCV', 'MCH', 'MCHC', 'PLT', 'RDW-SD', 'RDW-CV', 'PDW', 'MPV', 'P-LCR',
         'PCT', 'NEUT', 'LYMPH', 'MONO', 'EO', 'BASO', 'IG'])

    # Process each image in the directory
    for filename in os.listdir(image_directory):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(image_directory, filename)
            process_image(image_path, csv_writer)
            csvfile.flush()
        else:
            print(f"Ignoring file: {filename} (Unsupported format)")

print("Processing complete.")
