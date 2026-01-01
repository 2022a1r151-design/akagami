import socket
import json
import os
import sys

class ServiceVerifier:
    def __init__(self, timeout=5):
        self.timeout = timeout

    def grab_banner(self, ip, port):
        """
        Attempts to connect to a port and read the first few bytes (Banner).
        Returns the banner if successful, or None if it's a ghost/firewall.
        """
        try:
            # Create a raw socket (IPv4, TCP)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            
            # Connect
            result = s.connect_ex((ip, int(port)))
            
            if result == 0:
                # If connected, try to receive data immediately
                try:
                    # Send a dummy byte to trigger a response (for some protocols)
                    # HTTP needs a GET, others might just send a banner on connect
                    if port in [80, 443, 8080]:
                        s.send(b'HEAD / HTTP/1.0\r\n\r\n')
                    
                    banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
                    s.close()
                    
                    if banner:
                        return banner
                    else:
                        return "Open (No Data)" # Socket open, but silent
                except:
                    s.close()
                    return "Open (Silent)"
            else:
                s.close()
                return None # Connection failed
        except Exception as e:
            return None

    def run(self, json_file):
        """
        Iterates through the Attack Card and verifies each port.
        """
        if not os.path.exists(json_file):
            print(f"❌ Error: File not found: {json_file}")
            return

        print(f"[*] 🕵️ Verifying targets in: {os.path.basename(json_file)}")

        with open(json_file, 'r') as f:
            data = json.load(f)

        target_ip = data.get('ip')
        if not target_ip:
            # Fallback if IP is missing, resolve hostname
            try:
                target_ip = socket.gethostbyname(data['hostname'])
            except:
                print("❌ Could not resolve IP.")
                return

        # Iterate through ports
        verified_ports = []
        for port_info in data.get('open_ports', []):
            port = int(port_info['port'])
            service = port_info['service']
            
            print(f"    Testing Port {port} ({service})...", end="\r")
            
            banner = self.grab_banner(target_ip, port)
            
            if banner:
                print(f"    ✅ Port {port} is REAL. Banner: {banner[:30]}...")
                port_info['verified'] = True
                port_info['real_banner'] = banner
                verified_ports.append(port_info)
            else:
                print(f"    👻 Port {port} is a GHOST (Firewall Artifact).")
                port_info['verified'] = False

        # Update the JSON with truth
        data['open_ports'] = verified_ports # Only keep the real ones? Or mark them?
        # Let's keep all but mark them, so we know what we filtered
        
        output_file = json_file.replace('_parsed.json', '_verified.json')
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)

        print(f"\n[+] ✨ Verification Complete.")
        print(f"[+] 📂 Truth File saved: {output_file}")
        print(f"[+] 📉 Ghost Ports Eliminated: {len(data['open_ports']) - len(verified_ports)} filtered out (if you chose to remove them).")

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Auto-find the parsed JSON
    results_dir = r"C:\CTF CHallange\Akagami-v2\data\nmap_results"
    
    # Find the most recent PARSED json
    try:
        files = [os.path.join(results_dir, f) for f in os.listdir(results_dir) if f.endswith('_parsed.json')]
        if files:
            latest_file = max(files, key=os.path.getctime)
            verifier = ServiceVerifier()
            verifier.run(latest_file)
        else:
            print("❌ No parsed JSON found.")
    except Exception as e:
        print(f"❌ Error: {e}")