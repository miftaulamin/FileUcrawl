import urllib.request
import urllib.parse
import mimetypes
from html.parser import HTMLParser
import sys

class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_form = False
        self.current_form_action = None
        self.current_form_method = None
        self.file_upload_found = False
        self.file_upload_pages = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'form':
            self.in_form = True
            self.current_form_action = attrs_dict.get('action', '')
            self.current_form_method = attrs_dict.get('method', 'get')

        if self.in_form and tag == 'input':
            input_type = attrs_dict.get('type', '')
            if input_type == 'file':
                self.file_upload_found = True
                if self.current_form_action:
                    self.file_upload_pages.append((self.current_form_action, self.current_form_method))

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
        file_upload_pages = [(urljoin(self.url, page[0]), page[1]) for page in parser.get_file_upload_pages()]

        if not file_upload_pages:
            print(f"No file upload form found at {self.url}\n")
        else:
            print(f"\033[93mFile upload found at the following pages for {self.url}:\033[0m")
            for page, method in file_upload_pages:
                print(f"  - {page} ({method.upper()})")
            print()

        return file_upload_pages

    def test_file_upload(self, form_action, form_method):
        # Add your additional file upload vulnerability detection methods here
        pass

def print_banner():
    banner = """
███████╗██╗██╗     ███████╗██╗   ██╗ ██████╗██████╗  █████╗ ██╗    ██╗██╗     
██╔════╝██║██║     ██╔════╝██║   ██║██╔════╝██╔══██╗██╔══██╗██║    ██║██║     
█████╗  ██║██║     █████╗  ██║   ██║██║     ██████╔╝███████║██║ █╗ ██║██║     
██╔══╝  ██║██║     ██╔══╝  ██║   ██║██║     ██╔══██╗██╔══██║██║███╗██║██║     
██║     ██║███████╗███████╗╚██████╔╝╚██████╗██║  ██║██║  ██║╚███╔███╔╝███████╗
╚═╝     ╚═╝╚══════╝╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝
                                                                              
                                           
  \033[92mTool by Miftaul Amin\033[0m
"""
    print(banner)

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print("Usage: python FileUcrawler.py -l <websitelist.txt> [-o <outputfile.txt>]")
        sys.exit(1)

    print_banner()

    output_file = None
    if '-o' in sys.argv:
        output_index = sys.argv.index('-o')
        output_file = sys.argv[output_index + 1]
        sys.argv = sys.argv[:output_index] + sys.argv[output_index + 2:]

    if sys.argv[1] == '-l':
        try:
            with open(sys.argv[2], 'r') as f:
                urls = [line.strip() for line in f.readlines()]

            found_urls = []
            vulnerable_urls = []

            for url in urls:
                print(f"Checking website: {url}")
                finder = FileUploadFinder(url)
                file_upload_pages = finder.find_file_upload()

                if file_upload_pages:
                    found_urls.append(url)
                    for action, method in file_upload_pages:
                        if finder.test_file_upload(action, method):
                            vulnerable_urls.append(url)
                else:
                    print(f"No file upload form found at {url}\n")

            if output_file:
                with open(output_file, 'w') as f:
                    f.write("Websites with file uploading found:\n")
                    for url in found_urls:
                        f.write(f"{url}\n")
                    f.write("\nWebsites with potential vulnerabilities found:\n")
                    for url in vulnerable_urls:
                        f.write(f"{url}\n")

            print("\n**FileUcrawler**")
            print("Status: Completed")
        except FileNotFoundError:
            print("Error: The file specified does not exist.")
            sys.exit(1)
    else:
        print("Error: Invalid flag. Please use -l <websitelist.txt>")
        sys.exit(1)
