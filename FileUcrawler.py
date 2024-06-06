import requests
from bs4 import BeautifulSoup
import urllib.parse
import mimetypes
import sys
import re

class FileUploadCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.file_upload_pages = set()

    def crawl_and_scan(self, url=None, visited=None):
        if url is None:
            url = self.base_url
        if visited is None:
            visited = set()

        if url in visited:
            return

        visited.add(url)
        print(f"Visiting: {url}")

        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                forms = soup.find_all('form')
                print(f"Found {len(forms)} forms on {url}")

                for form in forms:
                    if form.find('input', {'type': 'file'}):
                        self.file_upload_pages.add(url)
                        print(f"File upload form found on {url}")
                        break

                links = soup.find_all('a', href=True)
                for link in links:
                    href = urllib.parse.urljoin(url, link['href'])
                    if href.startswith(self.base_url):
                        self.crawl_and_scan(href, visited)
        except Exception as e:
            print(f"Error accessing {url}: {e}")

    def get_file_upload_pages(self):
        return self.file_upload_pages

class FileUploadTester:
    def __init__(self, url):
        self.url = url

    def test_file_upload(self, form_action):
        files_to_test = {
            'php_shell.php': '<?php echo "Shell"; ?>',
            'php_shell.phtml': '<?php echo "Shell"; ?>',
            'php_shell.php3': '<?php echo "Shell"; ?>',
            'php_shell.php4': '<?php echo "Shell"; ?>',
            'php_shell.php5': '<?php echo "Shell"; ?>',
            'php_shell.php6': '<?php echo "Shell"; ?>',
            'php_shell.pht': '<?php echo "Shell"; ?>',
            'php_shell.pHp': '<?php echo "Shell"; ?>',
            'php_shell.PhP': '<?php echo "Shell"; ?>',
        }

        for filename, content in files_to_test.items():
            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
            data = (
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
                f'Content-Type: {mimetypes.guess_type(filename)[0] or "application/octet-stream"}\r\n\r\n'
                f'{content}\r\n'
                f'--{boundary}--\r\n'
            ).encode('utf-8')

            headers = {
                'Content-Type': f'multipart/form-data; boundary={boundary}'
            }

            try:
                response = requests.post(form_action, data=data, headers=headers)
                if "Shell" in response.text:
                    print(f"\033[91mVulnerability found: {filename} uploaded and executed on {self.url}\033[0m")
                    return True
            except Exception as e:
                print(f"Error during file upload test: {e}")

        return False

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

def urljoin(base, url):
    return urllib.parse.urljoin(base, url)

if __name__ == "__main__":
    print_banner()

    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print("Usage: python FileUcrawler.py -l <websitelist.txt> [-o <outputfile.txt>]")
        sys.exit(1)

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
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                print(f"Checking website: {url}")
                crawler = FileUploadCrawler(url)
                crawler.crawl_and_scan()

                file_upload_pages = crawler.get_file_upload_pages()
                if file_upload_pages:
                    found_urls.append(url)
                    print(f"\033[93mFile upload found at the following pages for {url}:\033[0m")
                    for page in file_upload_pages:
                        print(f"  - {page}")
                        tester = FileUploadTester(page)
                        if tester.test_file_upload(page):
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
