# Network Traffic Analysis Lab

This lab aims to analyze network traffic with wireshark and tcpdump tools. It demonstrate capturing packets techniques and security vulns detections. 
## What's This About?

The lab covers basics about network traffic analysis and shows how can unsecure and unencrypted protocols expose secure and sensitive data to the wild. I used two machines to analyse and capture the packets between them in the exercices. 
## Lab Exercises

### 1. Targeted Packet Capture
Captured traffic between specific hosts using tcpdump:
```bash
sudo tcpdump -i eth0 host 192.168.153.129 -w /tmp/target.pcap
```
Got 40 packets of TCP traffic saved successfully.

### 2. TCP Flow Analysis
Analyzed a complete TCP connection in Wireshark:
- Found an FTP connection (port 21)
- Identified the full 3-way handshake (SYN, SYN-ACK, ACK)
- Flow lasted about 8.74 seconds with 15 packets total

### 3. Credential Extraction (Security Issue!)
Connected via Telnet and captured the traffic. Using Wireshark's "Follow TCP Stream" feature, credentials were visible in plain text:
- Username: `msfadmin`
- Password: `msfadmin`

**This shows why you should never use unencrypted protocols like Telnet or FTP for anything important.**

### 4. Capture File Rotation
Set up automatic rotation for long-term monitoring:
```bash
sudo tcpdump -i eth0 -C 10 -W 5 -w /tmp/capture.pcap
```
Creates new files every 10MB and keeps only the last 5 files.


### 5. Detecting Suspicious Activity
Looked for network scans or unusual behavior. The captured traffic was clean - just normal FTP and Telnet connections.

**Two signs that might indicate a network scan:**
1. Lots of SYN packets hitting different ports from one IP with no responses
2. Rapid connection attempts to sequential ports (like 20, 21, 22, 23...)

## Tools Used
- **Wireshark** - for packet analysis and visualization
- **tcpdump** - for command-line packet capture
- **Metasploitable** - as the target machine

## Key Takeaways
- Unencrypted protocols expose everything (passwords, usernames, data)
- Packet analysis can reveal a lot about network behavior
- Always use encrypted alternatives (SSH instead of Telnet, SFTP/SCP instead of FTP)

## Setup
You'll need:
- Two networked machines or VMs
- Wireshark installed
- tcpdump (usually pre-installed on Linux)
- Root/sudo access for packet capture

---

**Date:** October 29, 2025  
