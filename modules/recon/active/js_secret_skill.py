import requests
import re
import sys
import json
import os
from urllib.parse import urljoin
from datetime import datetime

# 🎨 Color codes for hacker vibes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

# 🕵️ Secrets we are hunting for
PATTERNS = {
    "Tesla_ClientID": r'client_id["\']?\s*:\s*["\']([^"\']+)["\']',
    "Generic_API_Key": r'(api_key|apikey|access_token)["\']?\s*:\s*["\']([^"\']+)["\']',
    "Captcha_Config": r'captcha["\']?\s*:\s*\{\s*enabled\s*:\s*(false|true)',
    "Backend_URL": r'backendOrigin["\']?\s*:\s*["\']([^"\']+)["\']',
    "Sentry_DSN": r'dsn["\']?\s*:\s*["\'](https://[^"\']+)["\']'
}

def analyze_js(url, js_content):
    findings = {}
    print(f"{CYAN}[*] Scanning {url}...{RESET}")
    
    for name, pattern in PATTERNS.items():
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        if matches:
            findings[name] = matches
            print(f"{GREEN}[+] FOUND {name}: {matches}{RESET}")
            
    return findings

def get_js_files(target_url):
    print(f"{YELLOW}[*] Fetching HTML from {target_url}...{RESET}")
    try:
        # Spoof User-Agent to bypass simple WAFs
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(target_url, headers=headers, timeout=10, verify=False)
        
        # Regex to find <script src="...">
        js_links = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', response.text)
        
        full_links = []
        for link in js_links:
            # Handle relative URLs (e.g., /assets/index.js)
            full_url = urljoin(target_url, link)
            full_links.append(full_url)
            
        print(f"{CYAN}[*] Found {len(full_links)} JS files.{RESET}")
        return full_links
    except Exception as e:
        print(f"{RED}[!] Error fetching HTML: {e}{RESET}")
        return []

def scan_target(target):
    js_files = get_js_files(target)
    all_findings = {}

    for js_url in js_files:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(js_url, headers=headers, timeout=10, verify=False)
            findings = analyze_js(js_url, resp.text)
            
            if findings:
                all_findings[js_url] = findings
        except Exception as e:
            pass # Ignore read errors

    return all_findings

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <url>")
        sys.exit(1)

    target = sys.argv[1]
    
    # Disable SSL warnings for cleaner output
    requests.packages.urllib3.disable_warnings()
    
    results = scan_target(target)
    
    # Save results
    if results:
        domain = target.replace("https://", "").replace("http://", "").split('/')[0]
        
        # Consistent pathing logic
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        output_dir = os.path.join(base_dir, "data")
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"secrets_{domain}.json")
        
        with open(output_file, "w") as f:
            json.dump(results, f, indent=4)
        
        print(f"\n{GREEN}[SUCCESS] Secrets saved to {output_file}{RESET}")
    else:
        print(f"\n{YELLOW}[-] No secrets found.{RESET}")
