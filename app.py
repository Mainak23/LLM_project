from flask import Flask, Blueprint, request, jsonify,current_app
from werkzeug.utils import secure_filename
import os
from pdf2image import convert_from_path
import ollama
import json
import stat
import re
import json

model= 'llama3.2-vision'
app = Flask(__name__)
script_dir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(script_dir, "upload_folder")
CONVERT_FOLDER=os.path.join( script_dir,"convert_folder")

os.makedirs(UPLOAD_FOLDER,exist_ok=True)
os.makedirs(CONVERT_FOLDER,exist_ok=True)


ALLOWED_EXTENSIONS = {'pdf','PDF'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
directory_bp = Blueprint('directory', __name__)

def extract_invoice_details(text):
    # Step 1: Start printing when ** is found, remove commas
    text = re.sub(r',', '', text)

    # Step 2: Use regular expression to extract the key-value pairs
    matches = re.findall(r'\*\*(.*?)\*\*[\s:]*([^*]+)', text)
    
    # Step 3: Create the dictionary with key-value pairs
    result = {}
    for match in matches:
        key, value = match
        result[key.strip()] = value.strip()
    
    return result


class directory_oparation():
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.upload_folder=os.path.join( self.script_dir,"upload_folder")
        self.convert_folder=os.path.join( self.script_dir,"convert_folder")
    
    def Convert_pdf_to_image(self, pdf_file):
        for pdf_file in os.listdir(self.upload_folder):
            if pdf_file.endswith('.pdf'):  # Check if the file is a PDF
                pdf_path = os.path.join(self.upload_folder, pdf_file)
                images = convert_from_path(pdf_path)
                for page_num, image in enumerate(images):
                    output_filename = f"{os.path.splitext(pdf_file)[0]}_page_{page_num + 1}.png"
                    output_path = os.path.join(self.convert_folder, output_filename)
                    image.save(output_path, 'PNG')
                    print(f"Saved: {output_path}")
    def delete_files_in_directory(self):
        walk_upload = os.walk(self.upload_folder)
        walk_convert= os.walk(self.convert_folder)
        try:
            for (root1, _, files1), (root2, _, files2) in zip(walk_upload, walk_convert):
                for file1 in files1:
                    os.remove(os.path.join(root1, file1))
                    print(f"Removed: {os.path.join(root1, file1)}")
                for file2 in files2:
                    os.remove(os.path.join(root2, file2))
                    print(f"Removed: {os.path.join(root2, file2)}")
        except Exception as e:
            print(f"Error deleting files: {e}")
            
class read_file():
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.promt_path = os.path.join(self.script_dir, "promt_key.txt")
        self.file_content_key = open(self.promt_path, "r", encoding="utf-8", errors="ignore").read()
        self.content_key = self.file_content_key
        self.user = "user"
        self.model = "llama3.2-vision"  # Ensure 'model' is defined appropriately

    def result_ollama(self,input_file):
        response_key = ollama.chat(
            model=self.model,
            messages=[
                {
                    'role': self.user,
                    'content': self.content_key,
                    'images': [input_file]
                }
            ]
        )

        read_result = response_key.get('message', {}).get('content', None)
        
        # Replace control characters with commas
        read_preprocess = re.sub(r'[\t\n\r\v\f\a\b\0]', ',', read_result)
        print(f"{read_preprocess}_text")

        all_result = {}
        result = {}
        
        # Extract key-value pairs between ** and **
        matches = re.findall(r'\*\*(.*?)\*\*:\s*([^*]+)', read_preprocess)
        
        # Populate the dictionary with the matches
        for key, value in matches:
            result[key.strip()] = value.strip()
        
        # Add the extracted results to the final dictionary
        all_result["key_info"] = extract_invoice_details(read_preprocess)
        all_result["summary_result"] = read_preprocess
        print(all_result)

        return all_result  
     

# Directory operation backend class
class DirectoryOperationBackend:
    def __init__(self, app_context):
        self.upload_folder = app_context.config['UPLOAD_FOLDER']
    def read_folder(self):
        list_files = os.listdir(self.upload_folder)
        paths = [os.path.join(self.upload_folder, file) for file in list_files]
        return paths
    @staticmethod
    def allowed_file(filename):
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', set())
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    def upload_file(self, file):
        if file.filename == '':
            return "No file selected for upload", 400
        if self.allowed_file(file.filename):
            secure_name = secure_filename(file.filename)
            file_path = os.path.join(self.upload_folder, secure_name)
            file.save(file_path)
            return f"File '{secure_name}' uploaded successfully!", 200
        return "File type not allowed", 400
    


@directory_bp.route('/upload', methods=['POST'])
def upload_file():
    # Use current_app context to pass to DirectoryOperationBackend
    directory_operations = DirectoryOperationBackend(current_app)
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    message, status = directory_operations.upload_file(file)
    return jsonify({"message": message}), status

# Route to read the upload directory

@directory_bp.route('/convert', methods=['POST'])
def convert_pdf():
    make_obj_preprocess=directory_oparation()
    try:
        [make_obj_preprocess.Convert_pdf_to_image(pdf_file) for pdf_file in os.listdir(make_obj_preprocess.upload_folder)]
        return "convert sucsessfully",200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@directory_bp.route('/read', methods=['POST'])
def read_directory():
    try:
        # Create instances of the necessary classes
        make_obj_preprocess = directory_oparation()
        make_obj_detection = read_file()

        # Generate image paths
        image_path = [os.path.join(make_obj_preprocess.convert_folder, path) for path in os.listdir(make_obj_preprocess.convert_folder)]
        
        # Collect results for each image
        results = []
        for image in image_path:
            result_ = {
                "image_": image,
                "extracted_text": make_obj_detection.result_ollama(image)
            }
            results.append(result_)

        # Convert results to JSON format
        json_data = json.dumps(results, indent=4)
        return json_data

    except Exception as e:
        return jsonify({"error_dddd": str(e)}), 500

@directory_bp.route('/delete', methods=['DELETE'])
def delete_directory():
    make_obj_preprocess=directory_oparation()
    try:
        make_obj_preprocess.delete_files_in_directory()
        return "delete sucsessfull",200
    except:
        return "no file to delete",404


# Register the Blueprint with the Flask app
app.register_blueprint(directory_bp)

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)