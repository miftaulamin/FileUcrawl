import requests
from bs4 import BeautifulSoup
import sys

class FileUploadFinder:
    def __init__(self, urls):
        self.urls = urls

    def find_file_upload(self):
        for url in self.urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all the forms on the page
            forms = soup.find_all('form')

            # Iterate over the forms and check if they have a file input field
            for form in forms:
                inputs = form.find_all('input')

                for input in inputs:
                    if input.get('type') == 'file':
                        print(f"Found file upload form at {url}")

    def run(self):
        self.find_file_upload()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python file_upload_finder.py -l <websitelist.txt>")
        sys.exit(1)

    if sys.argv[1] == '-l':
        try:
            with open(sys.argv[2], 'r') as f:
                urls = [line.strip() for line in f.readlines()]
            finder = FileUploadFinder(urls)
            finder.run()
        except FileNotFoundError:
            print("Error: The file specified does not exist.")
            sys.exit(1)
    else:
        print("Error: Invalid flag. Please use -l <websitelist.txt>")
        sys.exit(1)