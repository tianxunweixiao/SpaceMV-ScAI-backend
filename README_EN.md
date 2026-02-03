# **ScAI Backend: TianXun Constellation Simulation and Integrated Management Platform Backend**
<div align="center">

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/tianxunweixiao/ScAI-Backend)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![ClickHouse](https://img.shields.io/badge/Database-ClickHouse-FFCC00?logo=clickhouse&logoColor=black)](https://clickhouse.com/)
[![Streamlit](https://img.shields.io/badge/Visual-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Deploy-Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

</div>

<img width="2564" height="1536" alt="Gemini_Generated_Image_7urlyp7urlyp7url" src="https://github.com/user-attachments/assets/b018204f-a95b-4f39-a104-1fda4432462f" />

`ScAI` is a constellation simulation and integrated management platform developed by Chengdu TianXun Microsatellite Technology Co., Ltd., designed to address the operational complexity challenges brought by the rapid expansion of constellation scale in the commercial space sector.

The platform adopts an Agent-oriented architecture design. The current open-source version focuses on building a high-precision orbital simulation calculation engine and data interaction foundation. It currently supports all-weather, all-region target area coverage simulation and resource scheduling for optical remote sensing satellites, laying a solid computing and data foundation for the future introduction of intelligent agents for automated task orchestration.

`ScAI Backend`, as the core server-side component of the platform, carries key functions including user request processing, simulation task execution, visualization service support, data storage management, and API interface distribution.

## **📖 Table of Contents**

* [Core Modules](#-core-modules)
* [Technical Architecture](#-technical-architecture)
* [Features](#-features)
* [Quick Start](#-quick-start)
* [API Documentation](#-api-documentation)
* [Troubleshooting](#-troubleshooting)
* [Contributing Guide](#-contributing-guide)
* [License](#-license)
* [Contact](#-contact)
* [To-Do List](#-to-do-list)

## **🧩 Core Modules**

ScAI Backend consists of the following four core modules:

| Module | Directory | Description |
| :---- | :---- | :---- |
| **Account Management Service** | account\_backend | Responsible for user authentication (JWT), permission management, and account security. |
| **Simulation Service** | serve\_backend | Core engine that handles satellite data management and STK coverage simulation analysis. |
| **Visualization Service** | visual\_backend | Visualization platform built on Streamlit, supporting tile maps and trajectory display. |
| **Data Synchronization** | timer.py | Scheduled task script responsible for synchronizing the latest satellite data from Celestrak API. |

## **🏗 Technical Architecture**

### **Directory Structure**

ScAI Backend/  
├── account\_backend/          \# 🔐 Account Management Service  
│   ├── app.py                \# FastAPI Application Entry  
│   ├── configs/              \# Configuration Management  
│   ├── controllers/          \# Route Controllers  
│   ├── services/             \# Business Logic Layer  
│   ├── models/               \# Data Models  
│   └── extensions/           \# Extension Modules  
│  
├── serve\_backend/            \# 🛰️ Simulation Service  
│   ├── app.py                \# FastAPI Application Entry  
│   ├── configs/              \# Configuration Management  
│   ├── controllers/          \# Route Controllers (satellites, constellations, sensors, simulation, LLM)  
│   ├── services/             \# Business Logic Layer  
│   ├── libs/                 \# Utility Libraries (simulation report generation)  
│   └── output/               \# Simulation Result Output Directory  
│  
├── visual\_backend/           \# 📊 Visualization Service  
│   ├── app\_tiles.py          \# Streamlit Application Entry (with tile maps)  
│   ├── app\_notiles.py        \# Streamlit Application Entry (without tile maps)  
│   └── tiles/                \# Map Tile Service  
│       ├── cors\_server.py    \# CORS Server  
│       └── gaode\_tiles/      \# Locally cached Gaode map tiles  
│  
├── stk\_scripts/              \# 🚀 STK Invocation Scripts  
│   ├── stk\_simulation.py     \# Coverage Analysis Execution Script  
│   └── stk\_backprogress.py   \# Data Processing Function Library  
│  
├── timer.py                  \# 🕒 Satellite Data Synchronization Timer  
├── requirements.txt          \# Project Dependencies  
└── .env.example              \# Environment Configuration Example File

### Technology Stack

| Domain | Technology Selection | Description |
| :--- | :--- | :--- |
| **Backend Framework** | **FastAPI** | High-performance asynchronous Web framework |
| | **Uvicorn** | ASGI server |
| | **Pydantic** | Data validation and configuration management |
| **Database** | **ClickHouse** | Stores massive satellite, constellation, and user data |
| **Visualization** | **Streamlit** | Rapid data application development |
| | **Plotly** | Interactive chart plotting |
| **Utility Components** | **Paramiko** | SSH client for remote STK invocation |
| | **APScheduler** | Scheduled task scheduling |
| | **STK Engine** | Satellite Tool Kit (requires separate license) |

### **Data Flow**

graph TD  
    A\[Celestrak API\] \--\>|Sync Data| B(timer.py Timer)  
    B \--\>|Write/Update| C\[(ClickHouse Database)\]  
    C \<--\>|Read/Write Data| D\[serve\_backend Simulation Service\]  
    D \--\>|Provide Data| E\[visual\_backend Visualization Service\]  
    E \--\>|Interactive Display| F\[User Interface\]

## **✨ Features**

### **1\. Account Management Service (account\_backend)**

**Port**: 5001

* 🔐 **Authentication Security**: Supports user registration, login, password encryption storage, and JWT token authentication.  
* 👤 **Status Management**: Complete account lifecycle management.  
* **API**: /api/login, /api/accountAdd

### **2\. Simulation Service (serve\_backend)**

**Port**: 8401

* 🛰️ **Satellite and Constellation Management**: Supports CRUD operations for satellites/constellations, and uploading custom constellation configurations.  
* 📡 **Sensor Management**: Configuration, query, and update of sensor parameters.  
* 🚀 **Simulation Execution**:  
  * Supports STK coverage analysis simulation (streaming output).  
  * **Hybrid Scheduling Mode**: Supports local execution or scheduling remote STK server execution via SSH.  
  * Automatically generates simulation reports.  
* 🤖 **LLM Integration**: Integrated with Ollama, providing AI-based conversational assistance.

### **3\. Visualization Service (visual\_backend)**

* 🌍 **2D Map Visualization**: Real-time rendering of satellite trajectories, sensor coverage envelopes, and target areas (points/lines/polygons).  
* 🗺️ **Tile Service**: Integrates custom or offline map tiles.  
* 📦 **Data Loading**: Supports automatic parsing and loading of simulation results from compressed packages or JSON.

### **4\. Data Synchronization (timer.py)**

* Automatically fetches the latest TLE data from Celestrak API.  
* Intelligently identifies and classifies constellations (GPS, Starlink, Beidou, etc.).  
* Automatically initializes database table structure and maintains data tables.

## **🚀 Quick Start**

### **Prerequisites**

* **Docker** (for deploying ClickHouse)  
* **STK Desktop (Windows) / STK Engine (Linux) 12.X**  
* Python environment with configured **STK agi package**

### **1. Environment Setup**
```bash
# Clone repository  
git clone https://github.com/tianxunweixiao/ScAI-backend.git   
cd ScAI-backend

# Create and activate Conda environment  
conda create -n scai python=3.12  
conda activate scai

# Install dependencies  
pip install -r requirements.txt
```
### **2. Initialize Database**
```bash
Start ClickHouse container and run synchronization script to initialize table structure and base data:

# Start ClickHouse  
docker run -d \  
--restart=always \
--log-opt max-size=1g \  
--log-opt max-file=10 \ 
--ulimit nofile=262144:262144 \  
-e CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1 \ 
-e CLICKHOUSE_DB=xingzuo \ 
-e CLICKHOUSE_USER=your_user \ 
-e CLICKHOUSE_PASSWORD=your_password \  
-p 9000:9000 \
-p 9004:9004 \
-p 8123:8123 \  
--name clickhouse clickhouse:25.3.6.56

# Initialize data  
python timer.py
```
### **3. Environment Variable Configuration**
```ini
Copy example file and modify configuration:

cp .env.example .env

Edit .env file, focus on configuring the following:

# ClickHouse Configuration  
CLICKHOUSE_HOST=your_clickhouse_host  
CLICKHOUSE_USER=your_user  
CLICKHOUSE_PASSWORD=your_password

# --- STK Simulation Configuration (Critical) ---  
# Mode A: Local Execution (STK and backend on the same machine)  
STK_LOCAL=True  
STK_PYTHON_LOCAL_EXE=C:\Path\To\python.exe  
STK_SCRIPT_LOCAL_PATH=D:\Path\To\stk_simulation.py

# Mode B: Remote Execution (Schedule remote STK server via SSH)  
STK_LOCAL=False  
STK_PYTHON_REMOTE_EXE=C:\Path\To\Remote\python.exe  
STK_SCRIPT_REMOTE_PATH=C:\Path\To\Remote\stk_simulation.py  
REPLACE_BASE=C:\Path\To\Project  # Project base path on remote server  
SSH_HOST=xxx  
SSH_USER=xxx  
SSH_PASSWORD=xxxxx

# LLM Configuration (currently only supports ollama framework)  
OLLAMA_URL=http://your_ollama_host:11434/api/chat
```
### **4. Start Services**
```bash
This project uses PM2 for process management:

# Install pm2  
npm install -g pm2

# Start all services  
pm2 start start_project.config.js

# View service status  
pm2 list
```

The ScAI client repository can be referenced at [ScAI-frontend](https://github.com/tianxunweixiao/ScAI-frontend).

## **📚 API Documentation**

After services start successfully, you can access the automatically generated interactive documentation:

* **Account Service**: [http://localhost:5001/docs](http://localhost:5001/docs)  
* **Simulation Service**: [http://localhost:8401/docs](http://localhost:8401/docs)

## **🔧 Troubleshooting**

| Issue | Possible Causes and Troubleshooting |
| :---- | :---- |
| **ClickHouse Connection Failed** | 1\. Check .env configuration. 2\. Confirm Docker container status (docker ps). 3\. Check if ports 8123/9000 are blocked by firewall. |
| **STK Simulation Failed** | 1\. Confirm STK License is valid. 2\. If using remote mode, check SSH connectivity and REPLACE\_BASE path mapping. 3\. Verify Python environment has agi.stk library correctly installed. |
| **No Data in Visualization** | 1\. Check if JSON files are generated in serve\_backend/output. 2\. Use browser F12 to check Console for parsing errors. |

## **🤝 Contributing Guide**

We warmly welcome community developers to participate in building ScAI Backend! If you have any improvement suggestions or discover bugs, please follow the following process:

1. **Fork this repository**: Click the Fork button in the upper right corner to copy the project to your GitHub account.  
2. **Create a branch**: Create a new branch from the main branch for development.  
   git checkout \-b feature/AmazingFeature  
3. **Commit changes**: Ensure code style is consistent and write clear Commit Messages.  
   git commit \-m 'feat: Add some AmazingFeature'  
4. **Push branch**:  
   git push origin feature/AmazingFeature  
5. **Submit Pull Request**: Initiate a PR on GitHub and describe your changes in detail.

**Development Suggestions**:

* When adding new APIs, please register routes in extensions/ext\_routers.py.  
* When adding new service logic, please follow the controller \-\> service \-\> model layered architecture.

## **📄 License**

This project is licensed under the **Apache License 2.0**.

Copyright (c) 2025 Chengdu TianXun Microsatellite Technology Co., Ltd.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

## **📮 Contact**

If you have any questions, suggestions, or business cooperation needs, please contact the project maintenance team.

* **Email**: code@spacemv.com  
* **Issues**: [GitHub Issues](https://github.com/tianxunweixiao/ScAI-backend/issues)

For more information, follow the company's WeChat official account:

<img width="106" height="106" alt="image" src="https://github.com/user-attachments/assets/69a02ad0-422c-422a-bf5f-9b7890cf31ab" />


## ✅ To-Do List

- [√] **Open Source Frontend Code**: Release the companion ScAI Frontend repository to implement a complete B/S architecture demonstration.
- [ ] **Introduce Intelligent Agents (Agent)**: Integrate AI Agents for automated constellation simulation task orchestration and scheduling.
- [ ] **Multi-Constellation Support**: Add preset support for navigation constellations and communication constellations.
- [ ] **STK Interface Enhancement**: Expand API coverage to support more fine-grained simulation parameter configuration
- [ ] **Improve Documentation**: Supplement detailed video tutorials and API interface use cases.
