# SSH Security & Hardening Lab

A practical lab on securing SSH access through configuration hardening, key-based authentication, and two-factor authentication (2FA). This covers everything from basic SSH setup to advanced security measures.

## What This Lab Covers

Worked through securing an SSH server step by step - from understanding the basics to implementing 2FA with Google Authenticator. The goal was to make remote access secure while keeping it usable.

## Lab Tasks

### Task 1: SSH Basics

**Q: What port does SSH listen on by default?**  
Port 22

**Q: What protocol version does SSH use?**  
SSH version 2 (v2) - much more secure than the old v1

### Task 2: Initial SSH Configuration

Modified the SSH config file (`/etc/ssh/sshd_config`):
- Uncommented `PermitRootLogin` and set it to `yes` (just for testing - we'll change this later)

### Task 3: Configuration Challenges

Went through several configuration scenarios to understand different SSH settings:

**Challenge 1: Enable Root Login**
```bash
PermitRootLogin yes
```

**Challenge 2: Change Default Port**
```bash
Port 666  # Changed from 22 to 666
```
(Non-standard ports add a tiny bit of security through obscurity)

**Challenge 3: Restrict Network Access**
```bash
ListenAddress 192.168.17.0/24
```
Only accepts connections from our specific network.

**Challenge 4: Disable Remote Root Login** (the right way)
```bash
PermitRootLogin no
```

**Challenge 5: Harden Authentication**
```bash
Protocol 2                    # Force SSH v2
PermitEmptyPasswords no       # No blank passwords
MaxAuthTries 3                # Only 3 login attempts
LoginGraceTime 30s            # 30 seconds to login
```

After each change, restarted SSH service:
```bash
sudo systemctl restart ssh
```

### Task 4: Key-Based Authentication

Generated SSH keys and set up key-based auth:

```bash
ssh-keygen -t rsa -b 4096
ssh-copy-id user@192.168.x.x
```

**Tested password login** - it was denied (as expected) because we switched to key-only auth.

**Why is key-based auth more secure than passwords?**

Key-based authentication is way more secure because:
- Keys are much longer and more complex than any password you'd remember
- Can't be brute-forced realistically (would take forever)
- Immune to phishing - you can't accidentally "type in" your private key somewhere
- No human error factor (weak passwords, reuse, etc.)

### Task 5: Additional Hardening

Applied extra security measures:

**Disable X11 Forwarding**
```bash
X11Forwarding no
```

**Disable User Environment Variables**
```bash
PermitUserEnvironment no
```
Prevents potential privilege escalation attacks.

**Restrict SSH in Firewall**
```bash
sudo ufw allow ssh
sudo ufw enable
```

**Enable fail2ban**
Automatically bans IPs after too many failed login attempts:
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Task 6: Monitoring Login Attempts

Checked for failed login attempts:

```bash
sudo journalctl _COMM=sshd | grep "Failed password"
```

(Note: Couldn't find the usual `/var/log/auth.log` file, so used journalctl instead)

No failed password attempts found in my case.

### Task 7: Two-Factor Authentication (2FA)

Set up Google Authenticator for an extra layer of security:

**1. Install Google Authenticator**
```bash
sudo apt-get install libpam-google-authenticator
```

**2. Configure for User**
```bash
google-authenticator
```
This generates QR codes you scan with your phone.

**3. Configure PAM** (`/etc/pam.d/sshd`)
Add at the top:
```bash
auth required pam_google_authenticator.so nullok
auth required pam_permit.so
```

**4. Configure SSH** (`/etc/ssh/sshd_config`)
```bash
ChallengeResponseAuthentication yes
AuthenticationMethods publickey,password publickey,keyboard-interactive
```

**5. Restart SSH**
```bash
sudo systemctl restart ssh
```

**How it works:**
- You need your SSH key AND a time-based code from your phone
- Even if someone steals your key, they can't login without the 2FA code
- Each code expires in 30 seconds

## Tools & Technologies

- **OpenSSH** - the SSH server and client
- **Google Authenticator** - for 2FA/TOTP codes
- **fail2ban** - automatic IP banning after failed attempts
- **ufw** - firewall management
- **journalctl** - system logging

## Security Improvements Made

Starting point → Hardened system:
- ✅ Disabled root login over SSH
- ✅ Changed to key-based authentication only
- ✅ Limited login attempts to 3
- ✅ Added 2FA requirement
- ✅ Enabled fail2ban for brute-force protection
- ✅ Restricted network access
- ✅ Disabled unnecessary features (X11, user env)

## Key Takeaways

- **Defense in depth** - multiple layers of security work better than one strong measure
- **Keys > Passwords** - always use key-based auth when possible
- **2FA is worth it** - adds significant security for minimal inconvenience
- **Monitor your logs** - failed attempts can indicate attacks
- **Default settings aren't secure** - always harden SSH on public-facing servers

## Common Mistakes to Avoid

1. Don't lock yourself out - test configs before closing your current session
2. Always keep a backup way in (console access, etc.)
3. Don't use weak passphrases on your SSH keys
4. Remember to update firewall rules when changing ports
5. Test 2FA thoroughly before logging out

## Setup Requirements

- Linux system with SSH server
- Root/sudo access
- Smartphone with authenticator app (for 2FA)
- Basic understanding of text editors (nano/vim)

---

**Date:** Lab 06  
**Group:** 01  
**System:** Kali 2025
