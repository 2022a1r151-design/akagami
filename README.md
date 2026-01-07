dsxa# 🏴‍☠️ Akagami v2 - Automated Reconnaissance Framework (Kali Linux Edition)

## 🚀 Overview
**Akagami v2** is a modular, high-performance reconnaissance framework built specifically for Kali Linux. It orchestrates industry-standard security tools through a Python-based "Skill" architecture, transforming raw OSINT data into prioritized, actionable targets for manual or automated exploitation.

Designed for bug hunters and red teamers, it handles the entire pipeline: from passive subdomain discovery to active vulnerability scanning and deep-dive JavaScript analysis.

---

## 📂 Project Architecture
The framework follows a strict data-driven model where and modules communicate via JSON outputs in a centralized directory.

```
akagami-v2/
├── config/             # Framework-wide configuration & READMEs
├── data/               # Centralized Data Lake (The Source of Truth)
│   ├── alive_hosts.json                # Verified live web targets
│   ├── <domain>_subdomains.json        # Raw passive discovery results
│   ├── secrets_<domain>.json           # Findings from JS analysis
│   ├── nmap_results/                   # Port scan & Nuclei outputs
│   │   ├── scan_<target>.xml           # Raw Nmap XML
│   │   ├── scan_<target>_parsed.json   # Processed port data
│   │   └── nuclei_vulns.json           # CVEs and Security Flaws
│   └── fuzzing_results/                # Directory brute-force logs
├── logs/               # Operations and runtime logs
└── modules/            # The "Skills" (Modular Python Wrappers)
    ├── recon/
    │   ├── passive/    # Discovery & Information Gathering
    │   └── active/     # Scanning, Fuzzing & Exploitation Discovery
```

---

## 🛠️ Prerequisites & Installation
Ensure the following tools are present in your system `$PATH`:

1.  **Orchestration**: `Python 3.10+`
2.  **Discovery**: `subfinder` (ProjectDiscovery)
3.  **Probing**: `httpx` (Binary version, installed in `/usr/local/bin/`)
4.  **Scanning**: `nmap`, `nuclei`
5.  **Brute-Force**: `ffuf` (v2.0+)

---

## 🎮 The Skill Sets (Detailed)

### 1. Passive Reconnaissance (`modules/recon/passive/`)

#### 🕵️ `subdomain_skill.py`
*   **Engine**: `subfinder`
*   **Function**: Performs multi-source passive subdomain enumeration.
*   **Command**: `python3 modules/recon/passive/subdomain_skill.py`

#### 📡 `httpx_skill.py`
*   **Engine**: `httpx` (Binary)
*   **Function**: Probes subdomains for HTTP/HTTPS liveness. Extracts titles, status codes, and server headers.
*   **Pathing**: Automatically reads from the latest subdomain JSON.
*   **Command**: `python3 modules/recon/passive/httpx_skill.py`

#### 📊 `analyzer_skill.py`
*   **Function**: Logic-driven analysis of `alive_hosts.json`.
*   **Value-Add**: Ranks targets as **"Green"** (200 OK, High Value) or **"Orange"** (Protected/Forbidden) based on status codes and titles.
*   **Command**: `python3 modules/recon/passive/analyzer_skill.py`

### 2. Active Reconnaissance & Vulnerability Discovery (`modules/recon/active/`)

#### ⚔️ `nmap_skill.py`
*   **Engine**: `nmap`
*   **Function**: Stealthy service versioning and port scanning on live hosts identified by the framework.
*   **Command**: `python3 modules/recon/active/nmap_skill.py`

#### 📝 `parser_skill.py` & `verifier_skill.py`
*   **Function**: The "Cleaning Crew." Converts Nmap XML into machine-readable JSON and validates data integrity before passing to the vulnerability scanner.
*   **Command**: `python3 modules/recon/active/parser_skill.py` | `python3 modules/recon/active/verifier_skill.py`

#### ☢️ `nuclei_skill.py`
*   **Engine**: `nuclei`
*   **Function**: Targeted vulnerability scanning. Uses custom tags for `api`, `token`, `misconfig`, and `exposure`.
*   **Filtering**: Automatically extracts targets from verified JSON files.
*   **Command**: `python3 modules/recon/active/nuclei_skill.py`

#### 🔨 `fuzzer_skill.py` (v2.0)
*   **Engine**: `ffuf`
*   **Advanced Features**: 
    - **Auto-Calibration (`-ac`)**: Smart filtering of noise.
    - **Recursion**: Crawls deeper into discovered directories.
    - **Multi-Arg Support**: Accepts direct URLs from CLI.
*   **Command**: `python3 modules/recon/active/fuzzer_skill.py <url>`

#### 🔍 `js_secret_skill.py`
*   **Function**: Scans remote targets, harvests all linked `.js` files, and analyzes them using regex for:
    - `Tesla_ClientID` / `API Keys`
    - `Sentry_DSN`
    - `Backend_URL` / `API Endpoints`
    - `Captcha_Config` (Finding disabled captchas)
*   **Command**: `python3 modules/recon/active/js_secret_skill.py <url>`

---

## 🔄 Standard Workflow (End-to-End)

1.  **Phase 1: Discovery**
    ```bash
    python3 modules/recon/passive/subdomain_skill.py  # Input: Domain
    python3 modules/recon/passive/httpx_skill.py      # Input: Subdomains List
    ```
2.  **Phase 2: Analysis & Selection**
    ```bash
    python3 modules/recon/passive/analyzer_skill.py   # Pick "Green Targets"
    ```
3.  **Phase 3: Deep Scan & Vuln Mapping**
    ```bash
    python3 modules/recon/active/nmap_skill.py        # Service Scan
    python3 modules/recon/active/parser_skill.py      # Format XML -> JSON
    python3 modules/recon/active/verifier_skill.py    # Match services to ports
    python3 modules/recon/active/nuclei_skill.py      # Run Nuclei Templates
    ```
4.  **Phase 4: Targeted Exploitation Discovery**
    ```bash
    python3 modules/recon/active/js_secret_skill.py <url> # Find hidden keys
    python3 modules/recon/active/fuzzer_skill.py <url>    # Enumerate paths
    ```

---

## 💡 Key Contributions & Features
- **Dynamic Path Resolution**: Every script calculates its location relative to the project root, allowing for execution from any directory.
- **WAF Bypass**: Custom headers and auto-calibration built into fuzzing and probing modules.
- **Targeted Scanning**: Modules are optimized to avoid "spraying and praying," focusing instead on verified live services.

---
*Developed by the Akagami Red Team*
