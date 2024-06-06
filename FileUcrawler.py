import requests
from bs4 import BeautifulSoup
import sys

class FileUploadFinder:
    def __init__(self, url):
        self.url = url

    def find_file_upload(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')

        forms = soup.find_all('form')

        found = False
        for form in forms:
            inputs = form.find_all('input')

            for input in inputs:
                if input.get('type') == 'file':
                    print(f"Found file upload form at {self.url}")
                    found = True
                    break

        if not found:
            print(f"No file upload form found at {self.url}")

    def run(self):
        self.find_file_upload()

    def find_vulnerability(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')

        input_field = soup.find('input', type='file')

        if input_field:
            mime_type = input_field.get('accept')
            if mime_type:
                if mime_type == 'application/pdf':
                    print(f"Vulnerability found: File upload is only allowed for PDF files ({self.url})")
                else:
                    print(f"Vulnerability found: File upload is allowed for multiple MIME types ({self.url})")
            else:
                print(f"Vulnerability found: No MIME type restriction found ({self.url})")
        else:
            print(f"No file input field found ({self.url})")

    def run_vulnerability(self):
        self.find_vulnerability()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main-code.py -l <websitelist.txt>")
        sys.exit(1)

    if sys.argv[1] == '-l':
        try:
            with open(sys.argv[2], 'r') as f:
                urls = [line.strip() for line in f.readlines()]
            for url in urls:
                finder = FileUploadFinder(url)
                finder.run()

                if finder.find_file_upload():
                    finder.run_vulnerability()
                else:
                    print(f"No file upload form found at {url}")
            print("\n\n**FileUcrawler**")
            print("Status: Completed")
        except FileNotFoundError:
            print("Error: The file specified does not exist.")
            sys.exit(1)
    else:
        print("Error: Invalid flag. Please use -l <websitelist.txt>")
        sys.exit(1)
