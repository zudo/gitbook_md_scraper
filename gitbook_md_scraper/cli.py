import os
import requests
import argparse
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
from collections import deque

# Configuration defaults
DEFAULT_OUTPUT_DIR = "docs"

def normalize_url(url):
    """Normalize URL by removing anchors and trailing slashes."""
    url = url.split('#')[0]
    return url.rstrip('/')

def sanitize_path_segment(segment):
    """Keep directory names filesystem friendly."""
    segment = unquote(segment.strip())
    sanitized = ''.join(ch if ch.isalnum() or ch in "-._" else '_' for ch in segment)
    sanitized = sanitized.replace(os.sep, '_')
    return sanitized or "root"


def build_output_directory(base_output_dir, start_url):
    """Nest downloads inside a folder derived from the start URL."""
    parsed = urlparse(start_url)
    segments = []

    if parsed.netloc:
        segments.append(parsed.netloc)

    path_parts = [part for part in parsed.path.strip('/').split('/') if part]
    if path_parts:
        segments.extend(path_parts)

    if not segments:
        segments.append("root")

    safe_segments = [sanitize_path_segment(part) for part in segments]
    return os.path.join(base_output_dir, *safe_segments)


def get_relative_path(url, start_url):
    """Extract the relative path from the URL to use as file path."""
    # Parse both URLs
    parsed_url = urlparse(url)
    parsed_start = urlparse(start_url)
    
    # Get the path relative to the start URL's path
    # We want to preserve the structure under the start path
    
    # Example:
    # Start: https://site.com/docs/foo
    # URL:   https://site.com/docs/foo/bar
    # Result: bar
    
    start_path = parsed_start.path.rstrip('/')
    url_path = parsed_url.path.rstrip('/')
    
    if url_path == start_path:
        return "README"
        
    if url_path.startswith(start_path):
        rel_path = url_path[len(start_path):].lstrip('/')
        return rel_path
        
    # Fallback for safety, though crawl logic should prevent this
    return url_path.lstrip('/')

def save_markdown(url, output_dir, start_url):
    """Try to download the .md version of the page."""
    md_url = url + '.md'
    try:
        response = requests.get(md_url)
        if response.status_code == 200:
            rel_path = get_relative_path(url, start_url)
            file_path = os.path.join(output_dir, rel_path + ".md")
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"[SUCCESS] Saved: {file_path}")
            return True
        else:
            # print(f"[SKIP] No Markdown found for: {url}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to save {url}: {e}")
        return False

def crawl(start_url, output_dir):
    start_url = normalize_url(start_url)
    output_dir = build_output_directory(output_dir, start_url)
    queue = deque([start_url])
    visited = set([start_url])
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print(f"Starting crawl from {start_url}...")
    print(f"Output directory: {output_dir}")

    while queue:
        current_url = queue.popleft()
        
        # 1. Save the content for the current URL
        save_markdown(current_url, output_dir, start_url)
        
        # 2. Fetch page to find more links
        try:
            response = requests.get(current_url)
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links
            for a in soup.find_all('a', href=True):
                href = a['href']
                
                # Handle relative links
                if href.startswith('/'):
                    parsed_start = urlparse(start_url)
                    base_domain = f"{parsed_start.scheme}://{parsed_start.netloc}"
                    href = base_domain + href
                elif not href.startswith('http'):
                    continue
                
                # Normalize
                href = normalize_url(href)
                
                # Check if it is a child of the start_url
                if href.startswith(start_url) and href not in visited:
                    visited.add(href)
                    queue.append(href)
                    
        except Exception as e:
            print(f"[ERROR] parsing {current_url}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Recursively download GitBook documentation as Markdown.")
    parser.add_argument("url", help="The URL to start crawling from (e.g., https://docs.example.com/section)")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT_DIR, help="Output directory for downloaded files")
    
    args = parser.parse_args()
    
    crawl(args.url, args.output)

if __name__ == "__main__":
    main()
