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
        except urllib.error.HTTPError as e:
            print(f"Error accessing {self.url}: \033[91mHTTP Error {e.code}: {e.reason}\033[0m")
            return []
        except urllib.error.URLError as e:
            print(f"Error accessing {self.url}: \033[91m{e.reason}\033[0m")
            return []
        except Exception as e:
            print(f"Unexpected error: \033[91m{e}\033[0m")
            return []

        content_type = response.headers.get('Content-Type')
        encoding = 'utf-8'

        if content_type and 'charset=' in content_type:
            encoding = content_type.split('charset=')[-1]

        try:
            page_content = response.read().decode(encoding, errors='ignore')
        except Exception as e:
            print(f"Error decoding page content: \033[91m{e}\033[0m")
            return []

        parser = FormParser()
        parser.feed(page_content)
        file_upload_pages = [(urllib.parse.urljoin(self.url, page[0]), page[1]) for page in parser.get_file_upload_pages()]

        if not file_upload_pages:
            print(f"No file upload form found at {self.url}\n")
        else:
            print(f"\033[93mFile upload found at the following pages for {self.url}:\033[0m")
            for page, method in file_upload_pages:
                print(f"  - {page} (\033[94m{method.upper()}\033[0m)")
            print()

        return file_upload_pages

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
    if len(sys.argv) < 3 or len(sys.argv) > 6:
        print("\033[91mUsage: python FileUcrawler.py -l <websitelist.txt> [--url <website_url>] [-o <outputfile.txt>]\033[0m")
        sys.exit(1)

    print_banner()

    output_file = None
    url_to_scan = None

    if '--url' in sys.argv:
        url_index = sys.argv.index('--url')
        url_to_scan = sys.argv[url_index + 1]
        sys.argv = sys.argv[:url_index] + sys.argv[url_index + 2:]

    if '-o' in sys.argv:
        output_index = sys.argv.index('-o')
        output_file = sys.argv[output_index + 1]
        sys.argv = sys.argv[:output_index] + sys.argv[output_index + 2:]

    if '-l' in sys.argv:
        list_index = sys.argv.index('-l')
        list_file = sys.argv[list_index + 1]
        with open(list_file, 'r') as f:
            urls = [line.strip() for line in f.readlines()]
    elif url_to_scan:
        urls = [url_to_scan]
    else:
        print("\033[91mError: Invalid flags provided. Please use -l <websitelist.txt> or --url <website_url>\033[0m")
        sys.exit(1)

    found_urls = []
    vulnerable_urls = []

    for url in urls:
        print(f"Checking website: \033[94m{url}\033[0m")
        finder = FileUploadFinder(url)
        file_upload_pages = finder.find_file_upload()

        if file_upload_pages:
            found_urls.append(url)
        else:
            print(f"No file upload form found at {url}\n")

    if output_file:
        with open(output_file, 'w') as f:
            f.write("\033[92mWebsites with file uploading found:\n\033[0m")
            for url in found_urls:
                f.write(f"{url}\n")
            f.write("\n\033[92mWebsites with potential vulnerabilities found:\n\033[0m")
            for url in vulnerable_urls:
                f.write(f"{url}\n")

    print("\n\033[92m**FileUcrawler**\033[0m")
    print("\033[92mStatus: Completed\033[0m")
