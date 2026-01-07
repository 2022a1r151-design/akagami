import xml.etree.ElementTree as ET
import json
import os
import sys

class NmapParserSkill:
    def run(self, xml_file):
        """
        Reads Nmap XML and extracts open ports/services into a clean JSON Attack Card.
        """
        if not os.path.exists(xml_file):
            print(f"❌ Error: File not found: {xml_file}")
            return None

        tree = ET.parse(xml_file)
        root = tree.getroot()

        # The Attack Card (Structure)
        host_data = {
            "ip": "",
            "hostname": "",
            "open_ports": []
        }

        # 1. Get Hostname & IP
        for host in root.findall('host'):
            # Get IP
            address = host.find('address')
            if address is not None:
                host_data["ip"] = address.get('addr')
            
            # Get Hostname
            hostnames = host.find('hostnames')
            if hostnames is not None:
                for hn in hostnames.findall('hostname'):
                    host_data["hostname"] = hn.get('name')
                    break # Just grab the first one

            # 2. Get Ports
            ports = host.find('ports')
            if ports is not None:
                for port in ports.findall('port'):
                    state = port.find('state')
                    if state is not None and state.get('state') == 'open':
                        port_id = port.get('portid')
                        protocol = port.get('protocol')
                        
                        # Get Service Details
                        service = port.find('service')
                        service_name = "unknown"
                        product = "unknown"
                        version = ""
                        
                        if service is not None:
                            service_name = service.get('name', 'unknown')
                            product = service.get('product', '')
                            version = service.get('version', '')

                        # Add to our Attack Card
                        host_data["open_ports"].append({
                            "port": port_id,
                            "protocol": protocol,
                            "service": service_name,
                            "banner": f"{product} {version}".strip()
                        })

        # 3. Save the Clean JSON
        # We save it in the same folder as the XML, but with .json extension
        output_file = xml_file.replace('.xml', '_parsed.json')
        
        with open(output_file, 'w') as f:
            json.dump(host_data, f, indent=4)

        print(f"[+] 🧠 Analysis Complete.")
        print(f"[+] 📄 Attack Card created: {output_file}")
        
        # Print a quick summary for you to see now
        print(f"\n--- 🎯 TARGET SUMMARY: {host_data['hostname']} ---")
        for p in host_data['open_ports']:
            print(f"   🔓 Port {p['port']} ({p['service']}): {p['banner']}")
            
        return output_file

# --- TEST BLOCK ---
if __name__ == "__main__":
    # We automatically find the last XML you scanned
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    results_dir = os.path.join(base_dir, "data", "nmap_results")
    
    # Find the most recent XML file in that folder
    try:
        files = [os.path.join(results_dir, f) for f in os.listdir(results_dir) if f.endswith('.xml')]
        if files:
            latest_file = max(files, key=os.path.getctime)
            parser = NmapParserSkill()
            parser.run(latest_file)
        else:
            print("❌ No XML files found to parse. Run the Nmap Skill first!")
    except Exception as e:
        print(f"❌ Error: {e}")