import subprocess
import json
import os
import shutil
import sys

class HTTPXSkill:
    def __init__(self):
        if os.name == 'nt':
            self.tool_name = "httpx.exe"
        else:
            # On Linux, especially Kali, 'httpx' can conflict with a Python library.
            # We check for httpx-toolkit (Kali name) or the standard httpx binary.
            self.tool_name = shutil.which("httpx-toolkit") or shutil.which("httpx")
            
            # If it's the wrong httpx (the python one), it won't have the -version flag we expect
            # but for now let's just ensure we found SOMETHING. 
            # Given we just installed it to /usr/local/bin, it should be found.
        
        if not self.tool_name or not shutil.which(self.tool_name):
            print(f"❌ Critical Error: HTTPX not found. Please install ProjectDiscovery's httpx.")
            sys.exit(1)

    def run(self, input_file):
        """
        Reads a list of subdomains from a JSON file and checks which ones are alive.
        """
        # 1. READ THE PREVIOUS DATA
        if not os.path.exists(input_file):
            print(f"❌ Error: Input file not found: {input_file}")
            return None
            
        # We need to extract just the hostnames from the Subfinder JSON
        domains = []
        try:
            with open(input_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    print("❌ Error: Input file is empty.")
                    return None
                
                # Try parsing as a single JSON object/array first
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, str):
                                domains.append(item)
                            elif isinstance(item, dict) and 'host' in item:
                                domains.append(item['host'])
                    elif isinstance(data, dict) and 'host' in data:
                        domains.append(data['host'])
                except json.JSONDecodeError:
                    # If that fails, try parsing as JSONL (one JSON object per line)
                    f.seek(0)
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                            if isinstance(entry, str):
                                domains.append(entry)
                            elif isinstance(entry, dict) and 'host' in entry:
                                domains.append(entry['host'])
                        except:
                            continue
        except Exception as e:
            print(f"❌ Error reading JSON: {e}")
            return None

        if not domains:
            print("❌ No domains found in the input file.")
            return None

        print(f"[*] 🧬 Loaded {len(domains)} potential targets. Starting LIVENESS PROBE...")

        # 2. CREATE A TEMP LIST FOR HTTPX TO READ
        # We write the domains to a temp text file because httpx likes reading text files
        temp_target_file = "temp_targets.txt"
        with open(temp_target_file, "w") as f:
            for domain in domains:
                f.write(f"{domain}\n")

        # 3. DEFINE OUTPUT
        # We save this in the same data folder
        output_dir = os.path.dirname(input_file)
        output_file = os.path.join(output_dir, "alive_hosts.json")

        # 4. RUN HTTPX
        # -title: Get the page title (helps us spot login pages)
        # -sc: Get status code (200, 403, 404)
        # -tech-detect: Identify technologies (Nginx, React, PHP) -> Crucial for AI analysis later
        command = [
            self.tool_name,
            "-l", temp_target_file,
            "-title",
            "-sc",
            "-tech-detect",
            "-json",  # Output as JSON
            "-o", output_file
        ]

        try:
            # We use shell=False for safety, but if it fails on Windows, you can try True
            subprocess.run(command, check=True, shell=False) 
            
            # CLEANUP
            if os.path.exists(temp_target_file):
                os.remove(temp_target_file)

            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                print(f"[+] 🎯 LIVENESS CHECK COMPLETE.")
                print(f"[+] 📂 Alive targets saved to: {output_file}")
                return output_file
            else:
                print("[-] ☠️ No live hosts found.")
                return None

        except subprocess.CalledProcessError as e:
            print(f"[!] Tool Failure: {e}")
            return None

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Point this to the file you just created!
    # Update "tesla.com_subdomains.json" if your filename is different
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    input_path = os.path.join(base_dir, "data", "tesla.com_subdomains.json")
    
    skill = HTTPXSkill()
    skill.run(input_path)