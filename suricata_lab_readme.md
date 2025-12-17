# Suricata IDS Lab - Network Intrusion Detection

A hands-on lab about setting up and configuring Suricata for network intrusion detection. This covers installing Suricata, writing custom rules, and testing different types of attacks.

## What I Did

This lab was all about learning how Suricata works as an IDS (Intrusion Detection System). I installed it, configured custom rules to detect various attacks, and then tested everything to make sure the rules were actually working.

## Lab Setup

### Step 1-3: Installing and Updating Suricata

First step was getting Suricata installed and updated:

```bash
sudo apt-get update
sudo apt-get install suricata
sudo suricata-update
```

Pretty straightforward - just standard installation process.

### Step 4: Running Suricata

Got Suricata running and did some initial tests:

```bash
sudo suricata -c /etc/suricata/suricata.yaml -i eth0
```

**Initial Tests:**
- Basic ping test - worked fine
- Tested with testmyids.org - successfully detected test alerts
- Confirmed logs were being written properly

## Custom Rules I Created

Added a bunch of custom detection rules to `/var/lib/suricata/rules/custom.rules`:

### Basic Detection Rules

**1. Example.com Access Detection**
```
alert http any any -> any any (msg:"Example.com Access Detected"; content:"example.com"; sid:1000001; rev:1;)
```
Simple rule to detect when someone visits example.com - good for testing.

**2. ICMP Ping Detection**
```
alert icmp any any -> any any (msg:"ICMP Echo Request Detected"; itype:8; sid:2000001; rev:1;)
```
Detects ping requests (ICMP type 8).

### SQL Injection Detection Rules

Created three rules to catch different SQL injection patterns:

**Rule 1: SELECT Statement**
```
alert http any any -> any any (msg:"SQL Injection Attempt - SELECT statement"; flow:to_server; content:"select"; nocase; http_uri; sid:3000001; rev:1;)
```

**Rule 2: UNION Statement**
```
alert http any any -> any any (msg:"SQL Injection Attempt - UNION statement"; flow:to_server; content:"union"; nocase; http_uri; sid:3000002; rev:1;)
```

**Rule 3: Generic SQL Syntax**
```
alert http any any -> any any (msg:"SQL Injection Attempt - Generic SQL syntax"; flow:to_server; content:"' or '1'='1"; nocase; http_uri; sid:3000003; rev:1;)
```

These catch the most common SQL injection techniques.

### SSH Brute Force Detection

```
alert tcp any any -> any 22 (msg:"Potential SSH Brute Force Attempt"; flow:to_server,established; detection_filter:track by_src, count 5, seconds 60; classtype:attempted-admin; sid:3000001; rev:1;)
```
Triggers if someone tries to connect to SSH more than 5 times in 60 seconds from the same IP.

### Suspicious Tool Detection

**SQLMap User-Agent**
```
alert http any any -> any any (msg:"Suspicious User-Agent Detected"; content:"sqlmap"; http_user_agent; nocase; sid:3000002; rev:2;)
```
Detects when someone's using SQLMap (a SQL injection tool).

### File Download Detection

```
alert http any any -> any any (msg:"Detect Executable File Download Over HTTP"; content:".exe"; http_uri; nocase; sid:3000003; rev:1;)
```
Alerts when someone downloads an .exe file over HTTP.

### Network Scanning Detection

**SYN Packet Detection**
```
alert tcp any any -> $HOME_NET any (msg:"LAB - TCP SYN"; flags:S; flow:stateless; sid:9900001; rev:2;)
```

**Port Scan Detection**
```
alert tcp any any -> $HOME_NET any (msg:"LAB - Port Scan (SYN threshold)"; flags:S; flow:stateless; detection_filter: track by_src, count 20, seconds 60; classtype:attempted-recon; sid:9901001; rev:1;)
```
Triggers if someone sends 20+ SYN packets in 60 seconds - likely a port scan.

### Web Application Rules

**PHP File Access**
```
alert http any any -> any any (msg:"Suspicious PHP File Access"; http.method; content:"GET"; http.uri; content:".php"; nocase; sid:3100001; rev:1;)
```

**JSON POST Requests**
```
alert http any any -> any any (msg:"HTTP POST Request with JSON Payload Detected"; flow:to_server,established; http.method; content:"POST"; http.content_type; content:"application/json"; nocase; sid:3000007; rev:1;)
```

### TLS/SSL Detection

```
alert tls any any -> any any (msg:"Weak TLS Certificate Detected - Small Key Size"; tls.cert_fingerprint; tls.cert_subject; tls_cert_notbefore; tls_cert_notafter; tls.cert_expired; sid:3000008; rev:1;)
```
Detects weak encryption certificates.

## Testing the Rules

After adding all the rules, I restarted Suricata and ran tests for each one:

### Example.com Test
```bash
curl http://example.com
```
✅ Successfully detected and logged

### Ping Test
```bash
ping localhost
```
✅ ICMP alerts showed up in logs

### SSH Brute Force Test
```bash
for i in {1..6}; do ssh testuser@localhost; sleep 1; done
```
Simulates multiple SSH connection attempts - rule triggered after 5 attempts.

### SQLMap Detection Test
```bash
curl -A "sqlmap/1.0" http://localhost
```
Successfully detected the SQLMap user agent.

### PHP File Access Test
```bash
curl "http://localhost/test.php?cmd=whoami"
```
Caught the suspicious PHP access attempt.

### Executable Download Test
```bash
wget http://localhost/test.exe
```
(Created a dummy test.exe file first)
Detected the .exe download attempt.

### JSON POST Test
```bash
curl -X POST http://localhost -H "Content-Type: application/json" -d '{"test":"data"}'
```
Successfully logged the JSON POST request.

### TLS Test
```bash
curl -k https://www.google.com
```
Checked TLS certificate properties.

## Challenges I Faced

The biggest challenge was getting the rule syntax right - small typos in Suricata rules can break everything. Also had to be careful with SID numbers to avoid conflicts (each rule needs a unique SID).

Another thing was tuning the detection thresholds. Setting the SSH brute force counter too low would cause false positives from normal retries.

## Log Files

All detections are logged in:
- `/var/log/suricata/fast.log` - quick alerts
- `/var/log/suricata/eve.json` - detailed JSON logs

You can watch alerts in real-time:
```bash
tail -f /var/log/suricata/fast.log
```

## Tools Used

- **Suricata** - the IDS itself
- **curl** - for testing HTTP rules
- **wget** - for testing downloads
- **ping** - for ICMP tests
- **ssh** - for brute force testing

## What I Learned

- How IDS rules work and how to write them
- Different attack patterns and how to detect them
- The importance of proper rule tuning (false positives vs false negatives)
- How network traffic inspection actually works
- That SQLMap has a very obvious user agent string

## Key Takeaways

- An IDS is only as good as its rules - you need to keep them updated
- Testing your rules is crucial - a rule that doesn't trigger is useless
- Detection thresholds matter a lot - too sensitive = false alarms, too loose = missed attacks
- Logs fill up fast when monitoring real traffic
- Some attacks are super easy to detect (like SQLMap), others need more complex rules

## Requirements

- Linux system (I used Ubuntu)
- Suricata installed
- Root/sudo access
- Network interface to monitor
- Basic understanding of network protocols

---

**Date:** Lab 09  
**Group:** 01  
**Student:** MADENE Meriem