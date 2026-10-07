# Network Traffic Analyzer   

A Python-based network traffic analysis tool that analyzes PCAP and PCAPNG files to visualize network activity and identify potentially suspicious traffic patterns.

## Features

- Analyze packet capture files (PCAP/PCAPNG).
- Visualize network protocol distribution.
- Identify top source and destination IP addresses.
- Analyze packet size distribution.
- Detect potential anomalies, such as an IP address accessing 100 or more distinct ports.
- Display analysis results through an interactive dashboard.

## Technology Stack

- Python
- Streamlit
- Scapy
- Pandas
- Plotly

## Getting Started

### Prerequisites

- Python 3.10 or newer
- pip

### Installation

Clone the repository:

```bash
git clone https://github.com/shreyassbhat508-cmd/Network_traffic_analyzer.git
cd Network_traffic_analyzer
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
streamlit run app.py
```

## Usage

1. Launch the application.
2. Upload a PCAP or PCAPNG file.
3. Analyze the captured network traffic.
4. Explore protocol statistics, IP addresses, packet sizes, and anomaly alerts.

## Disclaimer

This project is intended for educational purposes and authorized network traffic analysis. Anomaly alerts indicate potentially suspicious patterns and do not independently confirm malicious activity.

## Contributors

Developed as a hackathon project by our hackathon team.
