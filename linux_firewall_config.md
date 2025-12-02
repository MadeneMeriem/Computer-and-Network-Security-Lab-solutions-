# Advanced Firewall Configuration Lab

A practical lab on mastering Linux firewalls using both UFW (simple interface) and nftables (advanced framework). This covers everything from basic port filtering to anti-brute-force protection and intrusion detection.

## What This Lab Covers

Learned how to properly lock down a Linux system using two different firewall tools - UFW for quick setups and nftables for complex filtering rules. By the end, you can block attacks, rate-limit connections, and log suspicious activity.

## Tools Overview

### UFW (Uncomplicated Firewall)
Simple, user-friendly interface for managing iptables/nftables. Perfect for:
- Quick server protection
- Opening/closing ports
- Allowing specific IPs
- Blocking protocols

### nftables
The modern Linux firewall framework that replaced iptables. Better for:
- Advanced configurations
- Stateful filtering (tracking connection state)
- Complex matching rules
- Logging and monitoring
- Rate limiting

**Key Components:**
- **Table** - logical container (e.g., `inet`, `ip`)
- **Chain** - list of rules attached to a hook (input, output, forward)
- **Rule** - actual action (accept, drop, log, limit)

## Part 1: Initial Network Checks

Before configuring anything, check your network setup:

```bash
ip a                           # Show network interfaces
ping -c 4 <SERVER_IP>         # Test connectivity
ssh <SERVER_IP>               # Test SSH access
```

Make sure everything works before you start blocking stuff (don't lock yourself out!).

## Part 2: UFW Practice

### Basic UFW Commands

**Enable the firewall:**
```bash
sudo ufw enable
```

**Check status:**
```bash
sudo ufw status numbered
```

**Block ICMP (ping):**
```bash
sudo ufw deny proto icmp from any
```
Test from client - pings should fail now.

**Block SSH:**
```bash
sudo ufw deny 22/tcp
```
Try SSH from client - connection refused.

**Re-enable SSH:**
```bash
sudo ufw allow 22/tcp
```

**Delete a rule:**
```bash
sudo ufw status numbered      # Find the rule number
sudo ufw delete [NUM]         # Delete by number
```

### UFW Challenges

**Challenge 1: Block all incoming except ping**
```bash
sudo ufw default deny incoming
sudo ufw allow proto icmp
```

**Challenge 2: Allow only port 8080/tcp**
```bash
sudo ufw default deny incoming
sudo ufw allow 8080/tcp
```

**Challenge 3: Deny SSH from specific subnet**
```bash
sudo ufw deny from 192.168.1.0/24 to any port 22
```

## Part 3: nftables Advanced Practice

### Setup

**Install nftables:**
```bash
sudo apt install nftables -y
sudo systemctl enable nftables
sudo systemctl start nftables
```

### 3.1 Backup Current Rules

Always backup before making changes:
```bash
sudo nft list ruleset > backup.nft
```

### 3.2 Reset All Rules

Start fresh:
```bash
sudo nft flush ruleset
```

### 3.3 Create Table and INPUT Chain

Create the main firewall structure:
```bash
# Create the filter table
sudo nft add table inet filter

# Create INPUT chain with default DROP policy
sudo nft add chain inet filter input '{
  type filter hook input priority 0;
  policy drop;
}'
```

**What this does:** Drops all incoming traffic by default (whitelist approach).

### 3.4 Allow Loopback

Let local processes communicate:
```bash
sudo nft add rule inet filter input iif lo accept
```

The loopback interface (lo) is for internal communication - always allow it.

### 3.5 Allow Established Connections (Stateful Filtering)

Allow replies to connections you initiated:
```bash
sudo nft add rule inet filter input ct state established,related accept
```

**Stateful filtering** means the firewall remembers your outgoing connections and automatically allows the responses. Smart!

### 3.6 Allow SSH

Open SSH port:
```bash
sudo nft add rule inet filter input tcp dport 22 accept
```

### 3.7 SSH Rate Limiting (Anti Brute-Force)

Prevent password-guessing attacks:
```bash
sudo nft add rule inet filter input tcp dport 22 ct state new \
  limit rate 10/minute accept
```

This allows max 10 NEW SSH connections per minute. Brute-force attacks try hundreds per second, so this stops them cold.

### Logging Dropped Packets

See what's being blocked:
```bash
sudo nft add rule inet filter input limit rate 5/second \
  log prefix "FIREWALL_DROP: "
```

**View logs in real-time:**
```bash
sudo journalctl -f
```

This is super useful for debugging and detecting attacks.

## nftables Challenges

### Scenario 1: Block HTTP, Allow HTTPS

```bash
# Block HTTP
sudo nft add rule inet filter input tcp dport 80 drop

# Allow HTTPS
sudo nft add rule inet filter input tcp dport 443 accept
```

Test with:
```bash
curl http://SERVER_IP    # Should fail
curl https://SERVER_IP   # Should work
```

### Scenario 2: Allow Port Range (5000-5050)

```bash
sudo nft add rule inet filter input tcp dport 5000-5050 accept
```

Useful for services that use multiple ports (like FTP data transfers).

### Scenario 3: Block Specific Host

```bash
sudo nft add rule inet filter input ip saddr 192.168.1.100 drop
```

Blocks all traffic from that IP. Great for banning troublemakers.

### Scenario 4: Detect Nmap Scans

Add logging for common scan patterns:

```bash
# Log TCP SYN scans (most common)
sudo nft add rule inet filter input tcp flags syn \
  limit rate 10/second log prefix "POSSIBLE_SCAN: "

# Log NULL scans
sudo nft add rule inet filter input tcp flags == 0x0 \
  log prefix "NULL_SCAN: " drop

# Log XMAS scans
sudo nft add rule inet filter input tcp flags \& \(fin\|psh\|urg\) == fin\|psh\|urg \
  log prefix "XMAS_SCAN: " drop
```

Watch logs while someone runs:
```bash
nmap -sS SERVER_IP    # SYN scan
nmap -sN SERVER_IP    # NULL scan
nmap -sX SERVER_IP    # XMAS scan
```

You'll see the alerts in your logs!

## Common Commands Reference

### UFW Quick Reference

| Command | What It Does |
|---------|--------------|
| `sudo ufw enable` | Turn on firewall |
| `sudo ufw disable` | Turn off firewall |
| `sudo ufw status numbered` | Show rules with numbers |
| `sudo ufw allow PORT/proto` | Open a port |
| `sudo ufw deny PORT/proto` | Block a port |
| `sudo ufw delete NUM` | Remove rule by number |
| `sudo ufw reset` | Clear all rules |

### nftables Quick Reference

| Command | What It Does |
|---------|--------------|
| `sudo nft list ruleset` | Show all rules |
| `sudo nft flush ruleset` | Delete everything |
| `sudo nft add table ...` | Create table |
| `sudo nft add chain ...` | Create chain |
| `sudo nft add rule ...` | Add rule |
| `sudo nft delete rule ...` | Remove rule |

## Key Concepts

**Default Deny vs Default Allow:**
- **Default deny** (whitelist) - block everything, only allow what you specify (more secure)
- **Default allow** (blacklist) - allow everything, block specific things (easier but riskier)

**Stateful vs Stateless:**
- **Stateful** - firewall remembers connections, automatically allows replies
- **Stateless** - each packet judged independently, no memory

**Rate Limiting:**
Limits how many connections/packets per time period. Essential for preventing:
- Brute-force attacks
- DoS attacks
- Port scans

## Security Best Practices

1. **Always use default deny** - explicitly allow only what you need
2. **Enable rate limiting** on public services (SSH, HTTP, etc.)
3. **Log dropped packets** - helps detect attacks and troubleshoot issues
4. **Allow established connections** - don't break active connections
5. **Test before deploying** - use a VM or have console access
6. **Keep backup rules** - one wrong rule can lock you out
7. **Monitor logs regularly** - watch for unusual patterns

## Real-World Applications

- **Web servers** - allow 80/443, block everything else
- **SSH servers** - rate limit to prevent brute-force
- **Database servers** - only allow from app servers
- **Development machines** - open specific ports for testing
- **IoT devices** - extremely restrictive rules

## Common Mistakes to Avoid

❌ Forgetting to allow established connections - breaks outgoing requests  
❌ Not testing rules before disconnecting - can lock yourself out  
❌ Blocking loopback interface - breaks local services  
❌ No rate limiting on SSH - easy brute-force target  
❌ Default allow policy - one mistake exposes everything  

## Troubleshooting

**Can't connect after enabling firewall:**
- Check if you allowed the service: `sudo ufw status` or `sudo nft list ruleset`
- Make sure established connections are allowed
- Verify the port number is correct

**Rules not working:**
- Check rule order (first match wins)
- Verify chain hooks are correct
- Look for syntax errors: `sudo nft -c -f /etc/nftables.conf`

**Locked out via SSH:**
- Always have console/physical access as backup
- Test rules in a VM first
- Use `at` command to auto-disable firewall after delay:
  ```bash
  echo "ufw disable" | at now + 5 minutes
  ```

## Differences: UFW vs nftables

| Feature | UFW | nftables |
|---------|-----|----------|
| **Ease of use** | Very easy | More complex |
| **Flexibility** | Limited | Very flexible |
| **Performance** | Good | Better |
| **Learning curve** | 5 minutes | Few hours |
| **Best for** | Simple setups | Complex filtering |
| **Logging** | Basic | Advanced |

**When to use what:**
- **UFW** - personal servers, quick setups, simple rules
- **nftables** - production servers, complex filtering, performance-critical

## Testing Your Firewall

**From another machine:**
```bash
# Test ports
nmap -p 22,80,443 SERVER_IP

# Test ping
ping SERVER_IP

# Test specific service
telnet SERVER_IP 22
curl http://SERVER_IP
```

**Check logs:**
```bash
# Live monitoring
sudo journalctl -f

# Filter firewall logs
sudo journalctl | grep FIREWALL_DROP
```

---

**Lab:** 8 - Advanced Firewall Configuration  
**Tools:** UFW, nftables, iptables  
**Topics:** Stateful filtering, Rate limiting, Intrusion detection
