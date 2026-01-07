import subprocess
import json
import os
import shutil
import sys

class NucleiSkill:
    def __init__(self):
        self.tool_name = "nuclei.exe" if os.name == 'nt' else "nuclei"
        
        if not shutil.which(self.tool_name):
            print(f"❌ Critical Error: '{self.tool_name}' not found.")
            sys.exit(1)

    def extract_web_targets(self, json_file):
        """
        Reads the Verified JSON and extracts HTTP/HTTPS targets.
        """
        targets = []
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            ip = data.get('ip')
            hostname = data.get('hostname')
            target_host = hostname if hostname else ip

            if not target_host:
                return []

            for port_info in data.get('open_ports', []):
                port = int(port_info['port'])
                service = port_info['service']
                
                # Logic: If it's 80, assume http. If 443, assume https.
                # If Nmap said "http", trust it.
                if port == 80 or 'http' in service:
                    targets.append(f"http://{target_host}:{port}")
                elif port == 443 or 'ssl' in service or 'https' in service:
                    targets.append(f"https://{target_host}:{port}")
                    
        except Exception as e:
            print(f"❌ Error parsing JSON: {e}")
        
        return list(set(targets))

    def run(self, input_file):
        targets = self.extract_web_targets(input_file)
        
        if not targets:
            print("❌ No web targets found in the analysis file.")
            return

        print(f"[*] ☢️ Loading Nuclear Warheads against: {targets}")
        
        # 1. Save targets to a temp file for Nuclei
        target_list_file = "nuclei_targets.txt"
        with open(target_list_file, "w") as f:
            for t in targets:
                f.write(t + "\n")

        # 2. Prepare Output File
        output_dir = os.path.dirname(input_file)
        output_file = os.path.join(output_dir, "nuclei_vulns.json")

        # 3. THE COMMAND
        # -t: Use default templates
        # -s: Severity level (info, low, medium) -> We avoid 'critical' for now to be safe
        # -json: Output as JSON
        command = [
            self.tool_name,
            "-l", target_list_file,
            "-s", "info,low,medium",
            "-j",
            "-o", output_file
        ]

        try:
            # We explicitly update Nuclei templates first if needed, but let's just run.
            print("[*] ⏳ Scanning... (This might take a minute)")
            subprocess.run(command, check=True, shell=False)

            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                print(f"[+] 🚨 VULNERABILITIES FOUND.")
                print(f"[+] 📂 Report saved: {output_file}")
                
                # Quick Preview
                print("\n--- 🕵️ QUICK FINDINGS ---")
                with open(output_file, 'r') as f:
                    for line in f:
                        try:
                            vuln = json.loads(line)
                            print(f"   🔥 [{vuln['info']['severity'].upper()}] {vuln['info']['name']}")
                        except: pass
            else:
                print("[-] ✅ Clean. No obvious low/medium vulnerabilities found.")

        except subprocess.CalledProcessError:
            print("[!] Nuclei process failed.")
        finally:
            if os.path.exists(target_list_file):
                os.remove(target_list_file)

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Point this to your VERIFIED json
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    results_dir = os.path.join(base_dir, "data", "nmap_results")
    
    # Auto-find latest Verified or Parsed JSON
    try:
        files = [os.path.join(results_dir, f) for f in os.listdir(results_dir) if '_verified.json' in f or '_parsed.json' in f]
        if files:
            # Prefer verified if available
            latest_file = max(files, key=os.path.getctime)
            skill = NucleiSkill()
            skill.run(latest_file)
        else:
            print("❌ No target files found.")
    except Exception as e:
        print(f"❌ Error: {e}")