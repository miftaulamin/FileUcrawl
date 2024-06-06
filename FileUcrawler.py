import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

class FileUploadFinder:
    def __init__(self, url):
        self.url = url if url.startswith('http') else 'https://' + url

    def fetch_page(self, url):
        try:
            response = requests.get(url, verify=False)
            return response.text
        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}")
            return None

    def find_file_upload(self):
        page_content = self.fetch_page(self.url)
        if not page_content:
            return []

        soup = BeautifulSoup(page_content, 'html.parser')
        file_upload_pages = []

        # Method 1: Check input elements for file type
        for input_tag in soup.find_all('input', {'type': 'file'}):
            form = input_tag.find_parent('form')
            if form:
                action = form.get('action')
                action_url = urljoin(self.url, action) if action else self.url
                file_upload_pages.append(action_url)

        # Method 2: Check if form contains 'enctype' attribute with value 'multipart/form-data'
        for form_tag in soup.find_all('form'):
            if form_tag.get('enctype') == 'multipart/form-data':
                action = form_tag.get('action')
                action_url = urljoin(self.url, action) if action else self.url
                file_upload_pages.append(action_url)

        # Method 3: Check if form contains 'accept' attribute with value starting with 'image/' or 'application/'
        for form_tag in soup.find_all('form'):
            for input_tag in form_tag.find_all('input'):
                if input_tag.get('accept') and (input_tag['accept'].startswith('image/') or input_tag['accept'].startswith('application/')):
                    action = form_tag.get('action')
                    action_url = urljoin(self.url, action) if action else self.url
                    file_upload_pages.append(action_url)

        # Method 4: Check if form contains 'enctype' attribute with value 'application/x-www-form-urlencoded' and method 'POST'
        for form_tag in soup.find_all('form'):
            if form_tag.get('enctype') == 'application/x-www-form-urlencoded' and form_tag.get('method') == 'POST':
                action = form_tag.get('action')
                action_url = urljoin(self.url, action) if action else self.url
                file_upload_pages.append(action_url)

        if file_upload_pages:
            print(f"File upload found at the following pages for {self.url}:")
            for page in file_upload_pages:
                print(f"  - {page}")
        else:
            print(f"No file upload form found at {self.url}")

        return file_upload_pages

def print_banner():
    banner = """
    ███████╗██╗██╗     ███████╗██╗   ██╗ ██████╗██████╗  █████╗ ██╗    ██╗██╗     
██╔════╝██║██║     ██╔════╝██║   ██║██╔════╝██╔══██╗██╔══██╗██║    ██║██║     
█████╗  ██║██║     █████╗  ██║   ██║██║     ██████╔╝███████║██║ █╗ ██║██║     
██╔══╝  ██║██║     ██╔══╝  ██║   ██║██║     ██╔══██╗██╔══██║██║███╗██║██║     
██║     ██║███████╗███████╗╚██████╔╝╚██████╗██║  ██║██║  ██║╚███╔███╔╝███████╗
╚═╝     ╚═╝╚══════╝╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝
                                                                              
                                                                             
                                         \033[1;93mby MIFTAUL AMIN\033[0m
"""
    print(banner)

if __name__ == "__main__":
    print_banner()

    if len(sys.argv) != 3:
        print("Usage: python FileUcrawler.py -l <websitelist.txt>")
        sys.exit(1)

    if sys.argv[1] == '-l':
        try:
            with open(sys.argv[2], 'r') as f:
                urls = [line.strip() for line in f.readlines()]

            for url in urls:
                print(f"Checking website: {url}")
                finder = FileUploadFinder(url)
                finder.find_file_upload()
        except FileNotFoundError:
            print("Error: The file specified does not exist.")
            sys.exit(1)
    else:
        print("Error: Invalid flag. Please use -l <websitelist.txt>")
        sys.exit(1)
