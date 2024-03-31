# SOFAH Framework

The Speedy Open Framework for Automated Honeypot-development (SOFAH) is designed to facilitate the rapid and automated deployment of honeypots. By leveraging Docker, Python, and a suite of interconnected modules, SOFAH allows for the dynamic creation of honeypots tailored to simulate specific network environments and attract potential attackers.

## Getting Started

### Prerequisites

Before deploying SOFAH, ensure the following prerequisites are met:

- **Docker and Docker-Compose**: Installed on your system, with non-sudo user execution capability.
- **Python**: Version 3.10 installed.
- **SOFAH Utilities**: The `sofahutils` and `services` pip modules from the SOFAH repository must be installed.
- **GitHub OAuth Token**: Required for accessing SOFAH's GitHub repositories.
- **Operating System**: Developed on Linux; other OS compatibility not guaranteed.
- **Log Folder Permissions**: The directory for log files must allow read and write permissions for `others`.

### Starting SOFAH

To start SOFAH and automate the generation of a honeypot, adjust and execute the `sofah_starter.py` file from the main repository:

```python
if __name__ == "__main__":
    token = "github_tokentokentoken"  # Your GitHub OAuth Token
    log_folder_path = "/path/to/log/folder"  # Path to the log files directory
    endpoint_path = "/path/to/endpoints.json"  # Path to the endpoints JSON file
    ip_address = "0.0.0.0"  # The IP address of the target
    work_folder = "/in/this/folder/work/will/be/done"  # Working directory
    placeholder_vars = {"43LKDFSL": "<hostname>"}  # Placeholder variables for configuration
```

Replace all placeholders with meaningful values. After configuration, run the script.

Initially, the output will be verbose. Once the reconnaissance (Recon) module starts, there may be a quiet period of approximately 20 minutes where it appears that nothing is happening. This behavior is normal and expected during the Recon phase.

Following the completion of Recon, the ENrichment NORMalization (ENNORM) module will activate, processing and normalizing the Recon data into Docker container configurations for the honeypot services.

## Modules Overview

SOFAH is composed of several key modules, each serving a distinct purpose within the honeypot deployment process:

- **Recon**: Gathers preliminary data on potential targets and attack vectors.
- **ENNORM**: Processes Recon data to generate dynamic service configurations.
- **API Honeypot, Port Spoof, etc.**: Simulate various network services and behaviors to engage with attackers.
