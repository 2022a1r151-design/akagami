# 🏴‍☠️ Akagami v2 - Automated Reconnaissance Framework

## Overview
**Akagami v2** is a modular, Python-based reconnaissance framework designed to automate the offensive security pipeline. It orchestrates industry-standard tools to perform passive discovery, active scanning, and vulnerability assessment, transforming raw data into actionable intelligence.

The framework is designed for **Kali Linux** and follows a "Skill" based architecture where each script handles a specific phase of the kill chain.

## 📂 Project Structure
```
akagami-v2/
├── config/             # Configuration files
├── data/               # Centralized output directory
│   ├── alive_hosts.json                # Live web servers
│   ├── <domain>_subdomains.json        # Raw subdomains
│   ├── nmap_results/                   # Port scan & Nuclei results
│   └── fuzzing_results/                # Directory fuzzing results
├── logs/               # Operation logs
└── modules/            # Python "Skills" (Scripts)
    ├── recon/
    │   ├── passive/    # Discovery Phase
    │   └── active/     # Attack/Scan Phase
```

## 🛠️ Prerequisites
The framework relies on the following tools being installed and accessible in your system `$PATH`:

*   **Python 3.x** (Orchestration)
*   **Subfinder** (Passive Subdomain Enumeration)
*   **Httpx** (ProjectDiscovery) (Liveness Probing)
*   **Nmap** (Port Scanning)
*   **Nuclei** (Vulnerability Scanning)
*   **FFUF** (Directory Fuzzing)

## 🚀 Modules & Functionality

### 1. Passive Reconnaissance (`modules/recon/passive/`)

#### 👻 `subdomain_skill.py`
*   **Engine**: `subfinder`
*   **Purpose**: Harvests subdomains from passive sources (OSINT).
*   **Input**: Target Domain (e.g., `tesla.com`)
*   **Output**: `data/<domain>_subdomains.json`
*   **Command**: `python3 modules/recon/passive/subdomain_skill.py`

#### 🌐 `httpx_skill.py`
*   **Engine**: `httpx`
*   **Purpose**: Probes discovered subdomains to identify live web servers. Captures titles, status codes, and tech stacks.
*   **Input**: `data/<domain>_subdomains.json`
*   **Output**: `data/alive_hosts.json`
*   **Command**: `python3 modules/recon/passive/httpx_skill.py`

#### 📊 `analyzer_skill.py`
*   **Engine**: Python (Pandas/JSON)
*   **Purpose**: Analyzes `alive_hosts.json` to identify high-value targets. Filters for "Green" targets (Status 200) and interesting titles (Login, Dashboard, Admin).
*   **Output**: Console Report
*   **Command**: `python3 modules/recon/passive/analyzer_skill.py`

---

### 2. Active Reconnaissance (`modules/recon/active/`)

#### ⚔️ `nmap_skill.py`
*   **Engine**: `nmap`
*   **Purpose**: Performs service detection and version scanning on live hosts.
*   **Input**: `data/alive_hosts.json`
*   **Output**: `data/nmap_results/*.xml`
*   **Command**: `python3 modules/recon/active/nmap_skill.py`

#### 📝 `parser_skill.py`
*   **Engine**: Python (`xml.etree`)
*   **Purpose**: Converts complex Nmap XML reports into clean, machine-readable JSON.
*   **Input**: `data/nmap_results/*.xml`
*   **Output**: `data/nmap_results/*_parsed.json`
*   **Command**: `python3 modules/recon/active/parser_skill.py`

#### ✅ `verifier_skill.py`
*   **Engine**: Python
*   **Purpose**: Validates parsed data integrity before passing it to the vulnerability scanner.
*   **Input**: `data/nmap_results/*_parsed.json`
*   **Output**: `data/nmap_results/*_verified.json`
*   **Command**: `python3 modules/recon/active/verifier_skill.py`

#### ☢️ `nuclei_skill.py`
*   **Engine**: `nuclei`
*   **Purpose**: Scans verified targets for CVEs, misconfigurations, and security flaws.
*   **Input**: `data/nmap_results/*_verified.json`
*   **Output**: `data/nmap_results/nuclei_vulns.json`
*   **Command**: `python3 modules/recon/active/nuclei_skill.py`

#### 🔨 `fuzzer_skill.py`
*   **Engine**: `ffuf`
*   **Purpose**: Brute-forces directory paths on specific targets to find hidden resources.
*   **Features**: Auto-calibration (`-ac`), Recursion, Status Code Filtering (200, 403).
*   **Input**: Single URL (e.g., `https://admin.target.com`)
*   **Output**: `data/fuzzing_results/<domain>_fuzz.json`
*   **Command**: `python3 modules/recon/active/fuzzer_skill.py <url>`

## 🔄 End-to-End Workflow

1.  **Harvest**: Run `subdomain_skill.py` to build your target list.
2.  **Filter**: Run `httpx_skill.py` to find what's actually alive.
3.  **Prioritize**: Run `analyzer_skill.py` to pick your battles.
4.  **Scan**: Run the Active Pipeline (`nmap` -> `parser` -> `verifier`).
5.  **Attack**:
    *   Run `nuclei_skill.py` for automated vulnerability discovery.
    *   Run `fuzzer_skill.py` on specific "Green Targets" found by the Analyzer.

---
*Built with ❤️ for the Akagami Project*
