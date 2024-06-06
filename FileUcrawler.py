import urllib.request
from urllib.parse import urljoin
from html.parser import HTMLParser
import sys

class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_form = False
        self.current_form_action = None
        self.file_upload_found = False
        self.file_upload_pages = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'form':
            self.in_form = True
            self.current_form_action = attrs_dict.get('action', '')

        if self.in_form and tag == 'input':
            input_type = attrs_dict.get('type', '')
            if input_type == 'file':
                self.file_upload_found = True
                if self.current_form_action:
                    self.file_upload_pages.append(self.current_form_action)

    def handle_endtag(self, tag):
        if tag == 'form':
            self.in_form = False

    def get_file_upload_pages(self):
        return self.file_upload_pages

class FileUploadFinder:
    def __init__(self, url):
        self.url = url if url.startswith('http') else 'https://' + url

    def find_file_upload(self):
        try:
            print(f"Accessing URL: {self.url}")
            response = urllib.request.urlopen(self.url)
            content_type = response.headers.get('Content-Type')
            encoding = 'utf-8'
            
            if content_type and 'charset=' in content_type:
                encoding = content_type.split('charset=')[-1]

            page_content = response.read().decode(encoding, errors='ignore')
        except urllib.error.URLError as e:
            print(f"Error accessing {self.url}: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

        parser = FormParser()
        parser.feed(page_content)
        file_upload_pages = [urljoin(self.url, page) for page in parser.get_file_upload_pages()]

        if not file_upload_pages:
            print(f"No file upload form found at {self.url}")
        else:
            print(f"File upload found at the following pages:")
            for page in file_upload_pages:
                print(page)

        return file_upload_pages

    def find_vulnerability(self):
        try:
            print(f"Checking URL for vulnerabilities: {self.url}")
            response = urllib.request.urlopen(self.url)
            content_type = response.headers.get('Content-Type')
            encoding = 'utf-8'
            
            if content_type and 'charset=' in content_type:
                encoding = content_type.split('charset=')[-1]

            page_content = response.read().decode(encoding, errors='ignore')
        except urllib.error.URLError as e:
            print(f"Error accessing {self.url}: {e}")
            return
        except Exception as e:
            print(f"Unexpected error: {e}")
            return

        parser = FormParser()
        parser.feed(page_content)
        if parser.file_upload_found:
            print(f"Potential vulnerability found: File upload functionality exists at {self.url}")
        else:
            print(f"No file input field found ({self.url})")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python FileUcrawler.py -l <websitelist.txt>")
        sys.exit(1)

    if sys.argv[1] == '-l':
        try:
            with open(sys.argv[2], 'r') as f:
                urls = [line.strip() for line in f.readlines()]

            for url in urls:
                finder = FileUploadFinder(url)
                file_upload_pages = finder.find_file_upload()

                if file_upload_pages:
                    finder.find_vulnerability()
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
