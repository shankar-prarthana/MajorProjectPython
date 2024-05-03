import os

# Directory containing the files
directory = './Images/input'

# Get a list of all files in the directory
files = os.listdir(directory)

# Sort the files to ensure sequential numbering
files.sort()

# Initialize a counter for numbering
counter = 1

# Iterate through the files and rename them
for file in files:
    # Get the current file extension
    _, ext = os.path.splitext(file)

    # Generate the new filename with a number
    new_filename = f'{counter}{ext}'

    # Construct the full paths for the old and new filenames
    old_path = os.path.join(directory, file)
    new_path = os.path.join(directory, new_filename)

    # Rename the file
    os.rename(old_path, new_path)

    # Increment the counter
    counter += 1
