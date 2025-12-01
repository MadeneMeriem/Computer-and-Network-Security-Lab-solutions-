# Public Key Infrastructure (PKI) & Digital Certificates Lab

A hands-on lab covering the fundamentals of PKI - creating your own Certificate Authority (CA), generating SSL/TLS certificates, and deploying a secure HTTPS web server. This is how the internet's trust system actually works under the hood.

## What This Lab Is About

Ever wonder how HTTPS works? This lab walks through creating the entire certificate chain from scratch - from being your own CA to deploying a working HTTPS server. It's basically running your own mini version of Let's Encrypt or DigiCert.

## Prerequisites Setup

Before starting, need to modify OpenSSL's config to use our custom PKI structure:

Edit `/etc/ssl/openssl.cnf` (or `/usr/lib/ssl/openssl.cnf`) and update the `[ CA_default ]` section:

```bash
dir = /root/PKI
certificate = $dir/certs/ca.cert.pem
private_key = $dir/private/ca.key.pem
```

This tells OpenSSL where to find our CA files.

## Lab Steps

### Step 1: Create PKI Directory Structure

Set up the folder structure for managing certificates:

```bash
mkdir -p ~/PKI/{certs,crl,newcerts,private}
chmod 700 ~/PKI/private
touch ~/PKI/index.txt
echo 1000 > ~/PKI/serial
```

**What each folder does:**
- `certs/` - stores generated certificates
- `crl/` - Certificate Revocation Lists (for invalidated certs)
- `newcerts/` - newly issued certificates
- `private/` - private keys (locked down with 700 permissions)
- `index.txt` - database of issued certificates
- `serial` - tracks certificate serial numbers (starts at 1000)

### Step 2: Generate CA Private Key

Create the master key for your Certificate Authority:

```bash
openssl genrsa -aes256 -out ~/PKI/private/ca.key.pem 4096
chmod 400 ~/PKI/private/ca.key.pem
```

This creates a 4096-bit RSA key encrypted with AES-256. You'll set a passphrase - don't lose it! The `chmod 400` makes it read-only by owner.

### Step 3: Create CA Certificate

Generate the self-signed root certificate:

```bash
openssl req -x509 -new -key ~/PKI/private/ca.key.pem \
  -sha256 -days 3650 -out ~/PKI/certs/ca.cert.pem
```

You'll be prompted to enter details like:
- Country Name
- Organization Name
- Common Name (your CA name)

This certificate is valid for 10 years (3650 days) and is what you'll use to sign other certificates.

### Step 4: Generate Server Private Key

Create a key for your web server:

```bash
openssl genrsa -out server.key.pem 2048
sudo chown root:www-data server.key.pem
sudo chmod 640 server.key.pem
```

2048-bit is standard for server keys. The permissions let Apache read it.

### Step 5: Generate Server Certificate Signing Request (CSR)

Create a certificate request:

```bash
openssl req -new -key server.key.pem -out server.csr.pem
```

Fill in your server details. The **Common Name** should be your domain/hostname (e.g., `localhost` or `yourdomain.com`).

### Step 6: Sign Server Certificate with CA

Act as the CA and sign the server's certificate:

```bash
openssl ca -in server.csr.pem -out server.cert.pem -days 825 -notext
```

This creates a certificate valid for 825 days (about 2 years). Now your server has a cert signed by your CA!

**Inspect the certificate:**
```bash
openssl x509 -in server.cert.pem -noout -text
```

You can see all the details - issuer, subject, validity period, public key, etc.

### Step 7: Verify Certificate Chain

Make sure the certificate is properly signed:

```bash
openssl verify -CAfile ~/PKI/certs/ca.cert.pem server.cert.pem
```

Should return `server.cert.pem: OK` if everything's good.

### Step 8: Deploy HTTPS with Apache

**Install Apache (if needed):**
```bash
sudo apt install apache2
```

**Enable SSL module:**
```bash
sudo a2enmod ssl
sudo systemctl restart apache2
```

**Configure SSL** - edit `/etc/apache2/sites-available/default-ssl.conf`:

```apache
SSLEngine on
SSLCertificateFile /root/server.cert.pem
SSLCertificateKeyFile /root/server.key.pem
SSLCACertificateFile /root/PKI/certs/ca.cert.pem
```

**Enable the site:**
```bash
sudo a2ensite default-ssl.conf
sudo systemctl reload apache2
```

### Step 9: Test HTTPS

**Test with certificate verification:**
```bash
curl -v https://localhost
```

This will fail because your CA isn't trusted by curl.

**Test without verification:**
```bash
curl -vk https://localhost
```

The `-k` flag skips certificate verification. You should see the HTTPS connection work!

You can also test in a browser by visiting `https://localhost` - you'll get a security warning (expected, since your CA isn't in the system's trust store).

## Revocation Challenge

### How to Revoke a Certificate

Revoke the server certificate:

```bash
openssl ca -revoke server.cert.pem
openssl ca -gencrl -out ~/PKI/crl/ca.crl.pem
```

Update Apache config to use the CRL:
```apache
SSLCARevocationFile /root/PKI/crl/ca.crl.pem
```

Reload Apache and test - the certificate should now be rejected.

### Why You Can't Just Delete a Certificate

**Question:** "Why is simply removing the certificate from the server not enough to prevent fraudulent use?"

**Answer:** Because certificates are public documents. Once issued, copies exist everywhere:
- In browser caches
- On backup servers
- In certificate transparency logs
- Potentially with attackers

If someone got a copy of your certificate and private key, just removing it from YOUR server doesn't stop THEM from using it. That's why we need Certificate Revocation Lists (CRLs) and OCSP - to tell the world "this certificate is no longer trustworthy" even if it hasn't expired yet.

## Key Concepts Explained

**What's a Certificate Authority (CA)?**  
An entity that everyone trusts to verify identities. When a CA signs a certificate, they're saying "we verified that this key belongs to this domain/person."

**What's a CSR (Certificate Signing Request)?**  
A file containing your public key and identity info that you send to a CA for signing. The CA verifies your info, then signs it to create the actual certificate.

**What's the certificate chain?**  
Root CA → Intermediate CA(s) → Server Certificate. Browsers trust root CAs, and that trust flows down the chain.

**Why do certificates expire?**  
Security hygiene. Keys can be compromised over time, and expiration forces regular rotation. Also limits damage if a key is stolen.

## Real-World Applications

- **Web servers** - every HTTPS site uses this
- **Email encryption** - S/MIME certificates
- **Code signing** - proving software isn't tampered with
- **VPNs** - mutual authentication between client and server
- **IoT devices** - secure device identity

## Common Issues & Fixes

**"Unable to load CA private key"**  
- Check file paths in openssl.cnf
- Make sure you entered the correct passphrase

**"Certificate verification failed"**  
- CA cert path might be wrong
- Certificate might not be signed by the specified CA

**Apache won't start with SSL**  
- Check file permissions (Apache needs to read the key)
- Look at Apache error logs: `sudo tail -f /var/log/apache2/error.log`

**Browser shows "Not Secure"**  
- Expected! Your CA isn't in the browser's trust store
- For testing, you can import your CA cert into your browser/system

## Security Best Practices

- **Never share private keys** - especially the CA key
- **Use strong passphrases** on private keys
- **Limit CA key usage** - only use it to sign certificates, nothing else
- **Backup everything** - losing your CA key means starting over
- **Short validity periods** - 1-2 years max for server certs
- **Monitor for unauthorized certificates** - check your index.txt regularly

## Tools Used

- **OpenSSL** - cryptographic toolkit (basically THE tool for certificates)
- **Apache2** - web server with SSL/TLS support
- **curl** - for testing HTTPS connections

---

**Lab:** 7 - Public Key Infrastructure  
**Topics:** PKI, X.509 Certificates, TLS/SSL, Certificate Authority
