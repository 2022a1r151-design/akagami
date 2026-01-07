# Akagami v2 - Project Context

## 🧠 Project Philosophy
- **Modular Skills:** We use python wrappers in `modules/` rather than raw commands.
- **JSON Everything:** All tools must output JSON to `data/` for processing.
- **Verification First:** We verify targets (HTTP 200) before attacking.

## 🛠️ Tool Commands (The Skills)
- **Passive Recon:** `python3 modules/recon/passive/subdomain_skill.py`
- **Filter Live Hosts:** `python3 modules/recon/passive/httpx_skill.py`
- **Analyze Targets:** `python3 modules/recon/passive/analyzer_skill.py`
- **Active Fuzzing:** `python3 modules/recon/active/fuzzer_skill.py <url>`
- **JS Secret Discovery:** `python3 modules/recon/active/js_secret_skill.py <url>`
- **Port Scanning:** `python3 modules/recon/active/nmap_skill.py`
- **Parse Nmap Results:** `python3 modules/recon/active/parser_skill.py`
- **Verify Targets:** `python3 modules/recon/active/verifier_skill.py`
- **Vulnerability Scanning:** `python3 modules/recon/active/nuclei_skill.py`

## 📂 Architecture
- `data/alive_hosts.json`: The source of truth for targets.
- `data/<domain>_subdomains.json`: Raw subdomain enumeration results.
- `data/nmap_results/`: Port scanning and vulnerability scan outputs.
- `data/fuzzing_results/`: Directory brute-force results.
- `modules/`: Where the python logic lives.

## 🔄 Standard Workflow
1. **Harvest**: Run `subdomain_skill.py` to discover subdomains.
2. **Filter**: Run `httpx_skill.py` to identify live web servers.
3. **Prioritize**: Run `analyzer_skill.py` to find "Green Targets" (HTTP 200).
4. **Scan**: Run `nmap_skill.py` → `parser_skill.py` → `verifier_skill.py`.
5. **Attack**: Run `nuclei_skill.py` for vulns, `fuzzer_skill.py` for specific targets.

## 💡 Key Conventions
- Always use **absolute paths** when running scripts.
- Output files automatically save to the correct `data/` subdirectories.
- All modules support both interactive and command-line argument modes.
- The framework is designed for **Kali Linux** with all security tools pre-installed.
