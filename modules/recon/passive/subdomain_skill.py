import subprocess
import json
import os
import shutil
import sys

class SubdomainSkill:
    def __init__(self):
        # On Windows, we specifically look for the .exe
        self.tool_name = "subfinder.exe" if os.name == 'nt' else "subfinder"
        
        # Check if the tool is in the System PATH
        if not shutil.which(self.tool_name):
            print(f"❌ Critical Error: '{self.tool_name}' not found in PATH.")
            print("👉 Tip: If you downloaded it, add the folder location to your Windows Environment Variables.")
            sys.exit(1)

    def run(self, domain, output_dir=None):
        """
        Runs passive subdomain enumeration on a target domain.
        Returns a list of subdomains found.
        """
        if output_dir is None:
            # Automatically find the project's data directory
            # This goes up 3 levels from modules/recon/passive/ to akagami-v2/
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            output_dir = os.path.join(base_dir, "data")
        
        # Ensure data directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Define output file path
        output_file = os.path.join(output_dir, f"{domain}_subdomains.json")

        print(f"[*] 👻 Starting GHOST PHASE (Passive Recon) on: {domain}")

        # COMMAND CONSTRUCTION
        command = [
            self.tool_name,
            "-d", domain,
            "-all", 
            "-silent",
            "-oJ", 
            "-o", output_file
        ]

        try:
            # Run the command
            result = subprocess.run(command, capture_output=True, text=True, check=True, shell=False)
            
            # Parse the JSON output (subfinder -oJ produces JSON lines)
            subdomains = []
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                with open(output_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                data = json.loads(line)
                                if 'host' in data:
                                    subdomains.append(data['host'])
                            except json.JSONDecodeError:
                                pass
                
                # Save as a clean JSON array
                with open(output_file, 'w') as f:
                    json.dump(subdomains, f, indent=4)

            if subdomains:
                print(f"[+] ✅ Success! Found {len(subdomains)} subdomains. Data saved to: {output_file}")
                return subdomains
            else:
                print("[-] ⚠️ Warning: Tool ran, but found no subdomains.")
                return []

        except subprocess.CalledProcessError as e:
            print(f"[!] ❌ Tool Failure. Error Log:\n{e.stderr}")
            return []
        except FileNotFoundError:
             print(f"[!] ❌ System Error: Python cannot find '{self.tool_name}'. verify your PATH.")
             return []

# --- TEST BLOCK ---
if __name__ == "__main__":
    target = input("Enter target domain (e.g., tesla.com): ")
    skill = SubdomainSkill()
    # No output_dir passed, it will use the project's data folder automatically
    results = skill.run(target)
    
    if results:
        print(f"\n🔍 Found {len(results)} subdomains:")
        for sub in results[:10]: # Show first 10
            print(f"  - {sub}")
        if len(results) > 10:
            print(f"  ... and {len(results) - 10} more.")