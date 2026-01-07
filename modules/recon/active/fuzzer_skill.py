import subprocess
import json
import os
import shutil
import sys

class FuzzerSkill:
    def __init__(self):
        if not shutil.which("ffuf"):
            print("❌ Critical Error: 'ffuf' is not installed. Run: sudo apt install ffuf")
            sys.exit(1)
            
        # Kali Linux default wordlist location
        self.wordlist = "/usr/share/wordlists/dirb/common.txt"
        if not os.path.exists(self.wordlist):
            print(f"⚠️ Warning: Wordlist not found at {self.wordlist}. Please install wordlists (sudo apt install wordlists).")

    def run(self, url):
        """
        Runs FFUF against a single URL to find hidden directories.
        """
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        
        # Automatically find the project's data directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        output_dir = os.path.join(base_dir, "data", "fuzzing_results")
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"{domain}_fuzz.json")
        
        print(f"[*] 🔨 Fuzzing directory paths on: {url}")
        
        # COMMAND EXPLANATION:
        # -u: Target URL with FUZZ keyword (where to inject words)
        # -w: Wordlist path
        # -mc: Match codes (200 OK, 403 Forbidden)
        # -o: Output file
        # -of: Output format (json)
        # -t: Threads (40 is faster)
        # -ac: Auto-calibrate to filter out noise
        # -recursion: Scan recursively if a directory is found
        command = [
            "ffuf",
            "-u", f"{url}/FUZZ",
            "-w", self.wordlist,
            "-mc", "200,403",
            "-o", output_file,
            "-of", "json",
            "-t", "40",
            "-s", 
            "-ac",
            "-recursion"
        ]
        
        try:
            # We run the command
            subprocess.run(command, check=False) # check=False because ffuf returns non-zero on matches sometimes
            
            if os.path.exists(output_file):
                print(f"[+] 📂 Fuzzing complete. Data saved: {output_file}")
                self.analyze_results(output_file)
            else:
                print("[-] No interesting files found.")

        except Exception as e:
            print(f"[!] Error: {e}")

    def analyze_results(self, json_file):
        """Reads the FFUF JSON and prints the juicy finds"""
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                
            print("\n--- 🕵️ HIDDEN FILES FOUND ---")
            if 'results' in data:
                for result in data['results']:
                    print(f"   🔓 /{result['input']['FUZZ']} (Status: {result['status']})")
            else:
                print("   (No results in JSON)")
                
        except:
            pass

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Check if a URL was passed as a command-line argument
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        # Fallback to interactive input
        print("💡 Tip: You can also run this as: python3 fuzzer_skill.py <url>")
        target = input("Enter a URL to fuzz (e.g., http://target.com): ")
    
    if not target:
        print("❌ Error: No target URL provided.")
        sys.exit(1)
        
    if not target.startswith("http"):
        target = "http://" + target
        
    skill = FuzzerSkill()
    skill.run(target)