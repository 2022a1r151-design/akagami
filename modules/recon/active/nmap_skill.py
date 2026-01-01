import subprocess
import json
import os
import shutil
import sys

class NmapSkill:
    def __init__(self):
        # Check for Nmap
        self.tool_name = "nmap.exe" if os.name == 'nt' else "nmap"
        if not shutil.which(self.tool_name):
            print(f"❌ Critical Error: '{self.tool_name}' not found.")
            print("👉 Install it from https://nmap.org/download.html")
            sys.exit(1)

    def load_targets(self, json_file):
        """Reads the HTTPX JSON output and extracts targets"""
        targets = []
        try:
            with open(json_file, 'r') as f:
                # HTTPX output is usually a JSON list or JSON Lines
                # We try to read it as a JSON list first
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                         for entry in data:
                            # We prefer the 'host' or 'url' field
                            if 'host' in entry: targets.append(entry['host'])
                            elif 'url' in entry: targets.append(entry['url'])
                except json.JSONDecodeError:
                    # If that fails, try line-by-line (JSON Lines)
                    f.seek(0)
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            if 'host' in entry: targets.append(entry['host'])
        except Exception as e:
            print(f"❌ Error reading targets: {e}")
        
        # Remove duplicates
        return list(set(targets))

    def scan_target(self, target, output_dir):
        """Runs the actual Nmap scan on a single target"""
        
        # Clean target (remove http:// or https:// for Nmap)
        clean_target = target.replace("https://", "").replace("http://", "").split("/")[0]
        
        filename = f"scan_{clean_target}.xml"
        output_path = os.path.join(output_dir, filename)
        
        print(f"[*] 🚀 Launching Scan against: {clean_target}")

        # THE COMMAND (The Secret Sauce)
        # -sV: Probe open ports to determine service/version info
        # -sC: Run default scripts (finds obvious bugs)
        # -T4: Faster timing (T3 is normal, T4 is aggressive/fast)
        # -oX: Output as XML (Machine readable)
        command = [
            self.tool_name,
            "-sV", "-sC", "-T4",
            "-oX", output_path,
            clean_target
        ]

        try:
            subprocess.run(command, check=True, shell=False)
            print(f"[+] Scan saved: {output_path}")
        except subprocess.CalledProcessError:
            print(f"[!] Scan failed for {clean_target}")

    def run(self, input_file, limit=1):
        """Main execution flow"""
        targets = self.load_targets(input_file)
        
        if not targets:
            print("❌ No targets found to scan.")
            return

        print(f"[*] Found {len(targets)} live targets ready for interrogation.")
        print(f"[*] ⚠️ Safety Mode: Scanning only first {limit} targets.")

        output_dir = os.path.join(os.path.dirname(input_file), "nmap_results")
        os.makedirs(output_dir, exist_ok=True)

        # Loop through the targets (respecting the limit)
        for i, target in enumerate(targets[:limit]):
            self.scan_target(target, output_dir)
            
        print(f"\n[+] ✅ Batch Complete. Check the 'nmap_results' folder.")

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Point this to your ALIVE hosts file
    input_path = r"C:\CTF CHallange\Akagami-v2\data\alive_hosts.json"
    
    skill = NmapSkill()
    
    # We set limit=1 for the first test so you don't wait forever
    skill.run(input_path, limit=1)