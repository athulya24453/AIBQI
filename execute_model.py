import os
import subprocess
import sys

# Function to install packages
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# The rest of your script goes here...

import pandas as pd

# Path of the input image in the S3 bucket
img_path = "input"

import matplotlib.pyplot as plt

# Load the YOLOv8 model and perform inference
from ultralytics import YOLO
import cv2
import numpy as np
import json

# Load the trained YOLOv8 model
model = YOLO('Model/bestv1.pt')

# Load and preprocess the test image
def load_image(image_path):
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img, img_rgb

# Perform inference
def predict(image_path):
    img, img_rgb = load_image(image_path)
    results = model.predict(img_rgb)
    return results, img

# Collect port connection information and map port numbers correctly
import re
from collections import defaultdict

def collect_port_info(results):
    # Initialize a dictionary to store the port statuses
    port_info = defaultdict(lambda: "not connected")  # Default status is 'not connected'

    # Access the first result object (assuming single image inference)
    result = results[0]

    # Access the names dictionary from the result object
    names_dict = result.names

    # Get bounding boxes, scores, and class IDs from the result
    boxes = result.boxes.xyxy.cpu().numpy()
    scores = result.boxes.conf.cpu().numpy()
    cls = result.boxes.cls.cpu().numpy()

    # Process each detection and update the port info
    for score, cls_id in zip(scores, cls):
        # Get the class name (e.g., 'connected_port_1', 'n_connected_port_2')
        class_name = names_dict[int(cls_id)]

        # Extract the port number using regular expression (matches digits at the end of the string)
        port_number_match = re.search(r'(\d+)$', class_name)
        if port_number_match:
            port_number = int(port_number_match.group(1))  # Extract port number
            if "connected" in class_name.lower():
                port_info[port_number] = "connected"  # Set status as connected
            elif "n_connected" in class_name.lower():
                port_info[port_number] = "not connected"  # Set status as not connected

    # Convert port_info to a list of dictionaries, one for each port
    port_info_list = [{"port_number": port_num, "status": status} for port_num, status in port_info.items()]

    return port_info_list

# Process all images in a folder and save results as JSON
def process_folder_to_json(input_folder, output_folder):
    all_ports_info = []

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_folder, filename)
            results, _ = predict(image_path)  # Perform prediction on the image
            port_info = collect_port_info(results)  # Get port connection information

            # Append the data for each image
            all_ports_info.append({
                "image": filename,
                "ports": port_info  # List of port info dictionaries
            })

    return all_ports_info



# Set the input and output folders
main_dir = os.getcwd()
input_dir = os.path.join(main_dir, "input")
output_dir = os.path.join(main_dir, "output")

# Process the images and get port connection data as JSON
port_data = process_folder_to_json(input_dir, output_dir)

# Convert the port data to a JSON object
json_data = json.dumps(port_data, indent=4)

# Save the JSON object in the output folder
output_file_path = os.path.join(output_dir, "ports_data.json")

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Write the JSON data to a file
with open(output_file_path, "w") as json_file:
    json_file.write(json_data)

print(f"JSON data saved to {output_file_path}")

# Process images and annotate them
for filename in os.listdir(input_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join(input_dir, filename)
        results, _ = predict(image_path)
        
        # Set the path to save the annotated image
        output_image_path = os.path.join(output_dir, f"annotated_{filename}")

