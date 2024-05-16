import base64
from flask import Flask, request, jsonify, send_from_directory
import os
import re
from werkzeug.utils import secure_filename
from openai import OpenAI
import zipfile
import tempfile
from flask_cors import CORS

client = OpenAI()
app = Flask(__name__, static_folder='downloads')
CORS(app)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
@app.route('/generate-code', methods=['POST'])
def generate_code():
  if 'image' not in request.files:
    return jsonify({"error": "No file part"}), 400
  file = request.files['image']
  if file.filename == '':
    return jsonify({"error": "No selected file"}), 400
  if file:
    # Ensure filename is safe
    filename = secure_filename(file.filename)
    with tempfile.TemporaryDirectory() as tmpdirname:
        file_path = os.path.join(tmpdirname, filename)
        file.save(file_path)
        encoded_image = encode_image(file_path)
  try:
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Create framework java code well structured from this UML Diagram. Do not worry about implementation. Only return the Java Code"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=4096,
        )
  except Exception as e:
      # Here, returning a JSON response with error details and a 400 status code
      return jsonify({"error": "Invalid Image URL"}), 400

  text_response = response.choices[0].message.content

  java_code_start = text_response.find("java") + len("java\n")
  java_code_end = text_response.find("```", java_code_start)
  java_code = text_response[java_code_start:java_code_end].strip()
  # file_name = "GeneratedJavaCode.java"
  # with open(file_name, 'r') as file:
  #   # Read the entire file content into a string
  #   java_code = file.read()

  with tempfile.TemporaryDirectory() as tmpdirname:

    # Pattern to match class, interface, abstract class declarations
    class_pattern = r"(public\s+(?:class|abstract class|interface)\s+(\w+)[^\{]+?\{[\s\S]+?\n})"
    matches = re.findall(class_pattern, java_code)

    # Each match represents a separate class or interface
    for class_match in matches:
      class_name = class_match[1]
      class_code = class_match[0]
      file_name = f"{class_name}.java"
      with open(os.path.join(tmpdirname, file_name), "w") as file:
          file.write(class_code)
    
    path = 'backend/downloads'
    try:
      os.mkdir(path)
    except OSError as error:
      print("Skipping folder creation: folder already exists")

    zip_name = "generated_files.zip"
    zip_path = os.path.join(path, zip_name)  # Specify a path for the zip
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(tmpdirname):
            for file in files:
                zipf.write(os.path.join(root, file), file)
    return jsonify({"zip_url": f"/downloads/{zip_name}"})

@app.route('/downloads/<path:filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.static_folder, filename, as_attachment=True)
    
if __name__ == "__main__":
    app.run(debug=True)
  # completion = client.chat.completions.create(
  #   model="gpt-3.5-turbo",
  #   messages=[
  #     {
  #       "role": "system",
  #       "content": "At the end of each file, in between classes or interfaces, write 'end of file' as a delimeter for later parsing"
  #     },
  #     {
  #       "role": "user",
  #       "content": response  # Directly use the string here
  #     }
  #   ],
  #   max_tokens=4096,
  # )
  # gpt_output = completion.choices[0].message.content
  # print('out 3', gpt_output)
  # #gpt_output = '// Person.java\npublic class Person {\n    protected String name;\n    protected String phoneNumber;\n    protected String emailAddress;\n    \n    public void purchaseParkingPass() {\n        // implementation not provided\n    }\n\n    // Getters and setters for the fields would be here\n}\n// end of file\n\n// Student.java\npublic class Student extends Person {\n    private int studentNumber;\n    private int averageMark;\n    \n    public boolean isEligibleToEnroll() {\n        // implementation not provided\n        return false;\n    }\n\n    public int getSeminarsTaken() {\n        // implementation not provided\n        return 0;\n    }\n\n    // Getters and setters for the fields would be here\n}\n// end of file\n\n// Professor.java\npublic class Professor extends Person {\n    private int salary;\n    private int staffNumber;\n    private int yearsOfService;\n    private int numberOfClasses;\n\n    // Getters and setters for the fields would be here\n}\n// end of file\n\n// Address.java\npublic class Address {\n    private String street;\n    private String city;\n    private String state;\n    private int postalCode;\n    private String country;\n\n    public boolean validate() {\n        // implementation not provided\n        return false;\n    }\n\n    public String outputAsLabel() {\n        // implementation not provided\n        return null;\n    }\n\n    // Getters and setters for the fields would be here\n}\n// end of file\n"'
  # # print(gpt_output)

  # # Define the directory where you want to save the files
  # folder_path = 'files'  # Change this to the directory path on your local machine

  # # Make sure the directory exists
  # if not os.path.isdir(folder_path):
  #     os.makedirs(folder_path)

  # # Split the text by "end of file" markers
  # code_blocks = gpt_output.split("// end of file")

  # # Function to extract the class/interface name from a block of Java code
  # def extract_name(code_block):
  #     lines = code_block.strip().splitlines()
  #     # The class name is on the line before 'public class'
  #     for line in lines:
  #         if line.strip().endswith('.java'):
  #             return line.strip('// ').strip()

  # # Iterate over the code blocks and save each to a file
  # for block in code_blocks:
  #     block = block.strip()  # Remove leading/trailing whitespace
  #     if block:  # If there's code in the block
  #         name = extract_name(block)
  #         if name:
  #             file_path = os.path.join(folder_path, name)
  #             with open(file_path, 'w') as file:
  #                 file.write(block)
  #                 print(f"Saved {name}")

  # print(f"Java files have been generated in the folder: {folder_path}")