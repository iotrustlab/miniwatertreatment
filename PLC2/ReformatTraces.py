import json
import os

# Define the labels
doc_labels = ["treatmentComplete", "UnderFlowT2", "Valve201", "DoserYellow", "DoserBlue"]
ir_labels = ["ColorSensorRed", "ColorSensorGreen", "ColorSensorBlue", "RangeSensor201"]
hr_labels = ["Stage", "MaxDistanceFill", "MinDistanceFill"]

# Function to add labels to the data
def add_labels(data):
    for item in data:
        # Update the DIC to be an empty dictionary as required
        item["DIC"] = {}

        # Use dictionary comprehensions to add labels to DOC, IR, and HR
        item["DOC"] = {label: value for label, value in zip(doc_labels, item["DOC"])}
        item["IR"] = {label: value for label, value in zip(ir_labels, item["IR"])}
        item["HR"] = {label: value for label, value in zip(hr_labels, item["HR"])}
    return data

# Function to process a single JSON file
def process_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    modified_data = add_labels(data)
    return modified_data

# Function to process all JSON files in a folder
def process_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename)
            
            modified_data = process_file(input_file_path)
            
            with open(output_file_path, 'w') as f:
                json.dump(modified_data, f, indent=4)
            print(f"Processed {filename}")

# Specify the input folder containing the original JSON files
input_folder = "C:\\Users\\tardi\\OneDrive\\Documents\\Visual Studio Code Repos\\Python\\CPSWaterTestBench\\PLC2_Traces"

# Specify the output folder where modified JSON files will be saved
output_folder = "C:\\Users\\tardi\\OneDrive\\Documents\\Visual Studio Code Repos\\Python\\CPSWaterTestBench\\PLC2_Traces_Modified"

# Process all JSON files in the input folder
process_folder(input_folder, output_folder)
