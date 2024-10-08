from flask import Flask, request, jsonify, send_file
import os
import subprocess
import json

app = Flask(__name__)

# Define directories
input_dir = 'input'
output_dir = 'output'
model_script = 'execute_model.py'

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Check if the 'input' directory exists, create if not
        if not os.path.exists(input_dir):
            os.makedirs(input_dir)

        # Save the uploaded image in the "input" directory
        file = request.files['file']
        input_path = os.path.join(input_dir, file.filename)
        file.save(input_path)

        # Run the "execute_model.py" script
        process = subprocess.run(['python3', model_script], capture_output=True, text=True)

        # Check if the script ran successfully
        if process.returncode != 0:
            return jsonify({"error": "Model execution failed", "details": process.stderr}), 500

        # Success response
        return jsonify({"message": "Image processed and model executed successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_json', methods=['GET'])
def get_json():
    try:
        # Fetch the latest JSON file from the "output" directory
        output_file = os.path.join(output_dir, 'result.json')

        # Check if the JSON file exists
        if os.path.exists(output_file):
            # Return the JSON content to the front end
            with open(output_file, 'r') as f:
                json_data = json.load(f)
            return jsonify(json_data), 200
        else:
            return jsonify({"error": "JSON file not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
 


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)