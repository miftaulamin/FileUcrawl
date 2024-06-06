import requests
from bs4 import BeautifulSoup
import sys

class FileUploadFinder:
    def __init__(self, urls):
        self.urls = urls

    def find_file_upload(self):
        for url in self.urls:
            print(f"Scanning {url}...")
            try:
                response = requests.get(url)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            forms = soup.find_all('form')

            found = False
            for form in forms:
                inputs = form.find_all('input')

                for input in inputs:
                    if input.get('type') == 'file':
                        print(f"Found file upload form at {url}")
                        found = True
                        break

            if not found:
                print(f"No file upload form found at {url}")

    def run(self):
        self.find_file_upload()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main-code.py -l <websitelist.txt>")
        sys.exit(1)

    if sys.argv[1] == '-l':
        try:
            with open(sys.argv[2], 'r') as f:
                urls = [line.strip() for line in f.readlines()]
            finder = FileUploadFinder(urls)
            finder.run()
            print("\n\n**FileUcrawler**")
            print("Status: Completed")
        except FileNotFoundError:
            print("Error: The file specified does not exist.")
            sys.exit(1)
    else:
        print("Error: Invalid flag. Please use -l <websitelist.txt>")
        sys.exit(1)
