import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
def check_links(base_url):
    """
    Checks all links on a website for 404 errors and 302 redirects.
    Args:
        base_url: The base URL of the website to check.
    Returns:
        A pandas DataFrame containing the results.
    """
    results = []
    visited_pages = set()
    def crawl(url, parent_url):
        if url in visited_pages:
            return
        visited_pages.add(url)
        try:
            response = requests.get(url, allow_redirects=False, timeout=10)  # Set timeout to prevent indefinite hanging
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            if response.status_code == 302:
                results.append({"Link": url, "Status": response.status_code, "Parent Page": parent_url, "Redirected To": response.headers.get('Location')})
            elif response.status_code == 200:  # Only parse HTML if the response is OK
                soup = BeautifulSoup(response.content, "html.parser")
                for link in soup.find_all("a"):
                    href = link.get("href")
                    if href:
                        absolute_url = urljoin(url, href)  # Resolve relative URLs
                        if absolute_url.startswith(base_url): # Only check links within the same domain
                            crawl(absolute_url, url)
        except requests.exceptions.RequestException as e:
            if response and hasattr(response, 'status_code') and response.status_code == 404:
                results.append({"Link": url, "Status": response.status_code, "Parent Page": parent_url, "Redirected To": None})
            else:
                print(f"Error checking {url}: {e}")
    crawl(base_url, None)  # Start crawling from the base URL
    return pd.DataFrame(results)
if __name__ == "__main__":
    base_url = input("Enter the base URL of the website: ")
    df = check_links(base_url)
    # Print the DataFrame as a formatted table
    print(df.to_string())
    # Optionally save to a CSV file
    # df.to_csv("link_check_results.csv", index=False)
