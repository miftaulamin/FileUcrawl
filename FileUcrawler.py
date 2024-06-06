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
                            self.find_file_upload()
            except Exception as e:
                print(f"Error crawling {self.url}: {str(e)}")

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
        sys.exit(1)

    try:
        with open(sys.argv[2], 'r') as f:
            urls = [line.strip() for line in f.readlines()]

        found_urls = set()

        with ThreadPoolExecutor(max_workers=5) as executor:
            for url in urls:
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                print(f"\n\033[94mChecking website: {url}\033[0m")
                finder = FileUploadFinder(url)
                finder.find_file_upload()
                found_urls.update(finder.file_upload_pages)

        if found_urls:
            print("\n\033[93mFile upload found at the following pages:\033[0m")
            for page in found_urls:
                print(f"  - {page}")
        else:
            print("\nNo file upload form found on any of the provided websites.")

        print("\n\033[92m**FileUcrawler** by Miftaul Amin\033[0m")
        print("Status: Completed")
    except FileNotFoundError:
        print("Error: The file specified does not exist.")
        sys.exit(1)
