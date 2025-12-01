# Vulnerability Detection & Analysis Lab

A hands-on lab exploring vulnerability scanning and system hardening using Nikto and Lynis. This covers web application scanning, system auditing, and basic security hardening.

## What I Did

This lab walked through scanning a test system (Metasploitable) for vulnerabilities and then hardening it based on the findings. Used both web-focused and system-level security tools.

## Lab Exercises

### Step 1: Nikto Web Vulnerability Scan

Ran a comprehensive web server scan to find common vulnerabilities:

```bash
nikto -h http://192.168.153.129 -o nikto_report.txt -Format text
```

**Key Findings:**
- Directory indexing was enabled (not good - exposes file structure)
- Found services running on port 8181
- Tested with custom User-Agent strings to see server responses

Nikto basically checks for outdated software, misconfigurations, and known vulnerabilities in web servers.

### Step 2: Lynis System Audit

Did a full system security audit:

```bash
sudo lynis audit system
```

**Results:**
- **Hardening Index:** 60/100 (room for improvement)
- **5 Warnings** detected
- **38 Suggestions** for improvement

**Main Warnings Found:**
1. No password protection on certain services
2. Security repository missing from sources.list
3. Less than 2 responsive nameservers configured
4. Empty firewall ruleset
5. Can't find security repository in `/etc/apt/sources.list`

**Top 5 Recommendations:**
1. Update Lynis (current version is over 4 months old)
2. Install `libpam-tmpdir` for better session security
3. Install `libpam-usb` for multi-factor authentication
4. Install `apt-listbugs` to catch critical bugs before installing packages
5. Install `debian-goodies` to check which services need restarting after updates

### Step 3: Applying Fixes

Here are some of the fixes I implemented:

**1. Enable and Configure Firewall**
```bash
sudo ufw enable
sudo ufw default deny incoming
sudo ufw allow ssh
```

**2. Restrict SSH Root Login**
```bash
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart ssh
```

**3. Remove Unnecessary User Accounts**
```bash
cat /etc/passwd  # Check existing users
sudo userdel -r [username]  # Remove unused accounts
```

### Step 4: Network Monitoring

Checked what's actually running on the system:

```bash
sudo lsof -i -P -n  # Show all network connections
```

This shows which services are listening and what ports they're using.

**Firewall Status Check:**
```bash
sudo ufw status
```

Then enabled the firewall and verified SSH still works (important - don't lock yourself out!).

### Step 5: SUID Binary Analysis

Looked for SUID binaries (programs that run with elevated privileges):

```bash
find / -perm -4000 -type f 2>/dev/null  # Find SUID files
ls -la [binary]  # Check permissions
```

SUID binaries can be security risks if misconfigured or vulnerable, since they run with root privileges even when executed by regular users.

## Tools Used

- **Nikto** - web server vulnerability scanner
- **Lynis** - comprehensive system auditing tool
- **lsof** - lists open files and network connections
- **ufw** - uncomplicated firewall (Ubuntu's firewall manager)

## Main Vulnerabilities Found

- Directory indexing enabled on web server
- Firewall completely disabled
- SSH allowing root login
- Missing security updates repository
- Several unnecessary system accounts
- Weak PAM (authentication) configuration

## Security Recommendations

1. **Always run a firewall** - block everything by default, only allow what you need
2. **Disable root SSH** - use regular accounts with sudo instead
3. **Keep security repos enabled** - you need those security updates
4. **Regular audits** - run tools like Lynis periodically to catch new issues
5. **Minimize SUID binaries** - the fewer programs running as root, the better
6. **Clean up unused accounts** - old accounts are potential entry points

## Key Takeaways

- Automated scanners find a LOT of low-hanging fruit
- A hardening index of 60/100 is pretty typical for default installations
- Small misconfigurations (like directory indexing) can leak useful info to attackers
- Fixing basic stuff (firewall, SSH config) makes a huge difference

## Setup Requirements

- Linux system (I used Ubuntu/Metasploitable)
- Root/sudo access
- Nikto installed (`apt install nikto`)
- Lynis installed (`apt install lynis`)
- Network access to test system

---

**Date:** November 5, 2025  
**Group:** 01
