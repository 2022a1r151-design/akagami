import json
import os
import sys

class TargetAnalyzer:
    def run(self, input_file):
        if not os.path.exists(input_file):
            print(f"❌ File not found: {input_file}")
            return

        print(f"[*] 📊 Analyzing Intelligence from: {input_file}...")
        
        valid_targets = []
        
        try:
            with open(input_file, 'r') as f:
                # Handle JSONL (one JSON per line) which httpx often outputs
                for line in f:
                    if not line.strip(): continue
                    try:
                        data = json.loads(line)
                        
                        # Extract key data
                        url = data.get('url', 'unknown')
                        status = data.get('status_code', 0)
                        title = data.get('title', 'No Title')
                        tech = data.get('tech', [])
                        
                        # Store for sorting
                        valid_targets.append({
                            'url': url,
                            'status': status,
                            'title': title,
                            'tech': tech
                        })
                    except:
                        pass
        except Exception as e:
            print(f"❌ Error reading JSON: {e}")
            return

        # SORTING STRATEGY:
        # We want to see '200' codes first (most interesting), then others.
        valid_targets.sort(key=lambda x: x['status'])

        # DISPLAY DASHBOARD
        print("\n" + "="*100)
        print(f"{'STATUS':<8} | {'TITLE (Hint to Content)':<40} | {'URL':<50}")
        print("="*100)

        interesting_count = 0
        
        for t in valid_targets:
            # Color coding (ANSI escape codes) for Kali Terminal
            status_color = "\033[91m" # Red (Default)
            if t['status'] == 200: 
                status_color = "\033[92m" # Green (Target!)
                interesting_count += 1
            elif t['status'] in [301, 302]:
                status_color = "\033[93m" # Yellow (Redirect)
            elif t['status'] == 403:
                status_color = "\033[90m" # Grey (Likely Firewall)
            
            reset = "\033[0m"
            
            # Print row
            # We truncate title to 40 chars to keep table clean
            clean_title = (t['title'][:37] + '...') if len(t['title']) > 37 else t['title']
            print(f"{status_color}{t['status']:<8}{reset} | {clean_title:<40} | {t['url']}")

        print("="*100)
        print(f"[*] 🎯 Analysis Complete.")
        print(f"[*] Found {interesting_count} 'Green' targets (200 OK). ATTACK THESE FIRST.")

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Point this to the JSON file created by httpx_skill.py
    # Verify the path matches where you saved it!
    input_path = "/home/kali/Desktop/akagami-v2/data/alive_hosts.json"
    
    analyzer = TargetAnalyzer()
    analyzer.run(input_path)