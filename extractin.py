import os
import requests

class complete_application():
    def __init__(self):
        self.upload="hosting_adress/upload"
        self.convert="hosting_adress/convert"
        self.read="hosting_adress/read"
        self.delete="hosting_adress/delete"
 
       
    def upload_file(self,file_path):
        try:
            file_name = os.path.basename(file_path)
            url = self.upload
            files = [
                ('file', (file_name, open(file_path, 'rb'), 'application/pdf'))
            ]
            headers = {}
            response = requests.post(url, headers=headers, files=files)
            return response.text
        except FileNotFoundError:
            return "Error: File not found. Please check the file path."
        except Exception as e:
            return f"An error occurred: {e}"
       
    def convert_file(self):
        try:
            url=self.convert
            payload = {}
            files={}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            return response.text
        except Exception as e:
            return f"An error occurred: {e}"
       
    def read_file(self):
        try:
            url=self.read
            payload = {}
            files={}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            return print(response.text)
        except Exception as e:
            return f"An error occurred: {e}"
       
    def delete_file(self):
        try:
            url=self.delete
            payload = {}
            files={}
            headers = {}
            response = requests.request("DELETE", url, headers=headers, data=payload, files=files)
            return response.text
        except Exception as e:
            return f"An error occurred: {e}"
       
 
 
# Example usage
path = r"C:\Users\USER\Desktop\api_file_download\ocr_oddo_integration\B1002404483.pdf"
 
obj_1=complete_application()
obj_1.upload_file(path)
obj_1.convert_file()
result_1=obj_1.read_file()
obj_1.delete_file()
 
print(result_1)


