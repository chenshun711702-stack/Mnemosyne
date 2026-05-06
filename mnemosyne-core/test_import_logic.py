import requests
import json
import os

def test_import():
    url = "http://127.0.0.1:8000/import"
    # Adjusted path to project root
    file_path = "../historical memory/Bill_家庭档案_JSON版_20260505.json"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        # Try absolute path just in case
        file_path = os.path.abspath(os.path.join(os.getcwd(), "..", "historical memory", "Bill_家庭档案_JSON版_20260505.json"))
        if not os.path.exists(file_path):
            print(f"Still not found: {file_path}")
            return

    with open(file_path, "rb") as f:
        files = {"file": ("test.json", f, "application/json")}
        response = requests.post(url, files=files)
        
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_import()
