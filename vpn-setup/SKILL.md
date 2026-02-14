---
name: vpn-setup
description: Set up an OpenVPN server on GCP for secure access from China. Use when the user wants to create a VPN server, configure OpenVPN, or generate client configurations for bypassing network restrictions.
---

# OpenVPN Setup on GCP

Set up an OpenVPN server on Google Cloud Platform for secure, unrestricted internet access.

## Step 1: Create GCP VM

```bash
# Create VM in Asia region (Taiwan - close to China)
gcloud compute instances create proxy-server \
  --zone=asia-east1-b \
  --machine-type=e2-micro \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=10GB \
  --tags=https-server \
  --metadata=enable-oslogin=true
```

## Step 2: Create Firewall Rules

```bash
# Allow HTTPS traffic
gcloud compute firewall-rules create default-allow-https \
  --allow=tcp:443 \
  --target-tags=https-server \
  --description="Allow HTTPS traffic"

# Allow OpenVPN traffic (UDP 1194)
gcloud compute firewall-rules create allow-openvpn \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=udp:1194 \
  --source-ranges=0.0.0.0/0 \
  --description="Allow OpenVPN traffic"

# Alternative: Use TCP 443 to disguise as HTTPS
gcloud compute firewall-rules create allow-openvpn-tcp \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --description="Allow OpenVPN over TCP 443"
```

## Step 3: Install OpenVPN

```bash
# SSH into the VM
gcloud compute ssh proxy-server --zone=asia-east1-b

# Run OpenVPN install script (on the VM)
curl -O https://raw.githubusercontent.com/angristan/openvpn-install/master/openvpn-install.sh
chmod +x openvpn-install.sh
sudo ./openvpn-install.sh
```

Follow the prompts:

- Protocol: UDP (or TCP if disguising as HTTPS)
- Port: 1194 (or 443)
- DNS: Cloudflare or Google
- Client name: your-device-name

## Step 4: Download Client Config

```bash
# Copy .ovpn file from VM to local machine
gcloud compute scp proxy-server:~/client-name.ovpn . --zone=asia-east1-b
```

## Step 5: Install Client

### macOS (Recommended: Tunnelblick)

```bash
# Install via Homebrew
brew install --cask tunnelblick

# Or download from: https://tunnelblick.net/downloads.html
```

After installation:

1. Double-click the `.ovpn` file to import
2. Click "Only Me" when prompted
3. Click the Tunnelblick icon in menu bar → Connect

### macOS (Alternative: OpenVPN Connect)

```bash
brew install --cask openvpn-connect
```

### macOS (CLI only)

```bash
# Install OpenVPN CLI
brew install openvpn

# Connect (runs in foreground)
sudo openvpn --config ~/path/to/client.ovpn

# Or run as daemon
sudo openvpn --config ~/path/to/client.ovpn --daemon
```

### Windows

1. Download OpenVPN GUI: https://openvpn.net/community-downloads/
2. Install and run as Administrator
3. Import `.ovpn` file via right-click on system tray icon

### iOS / Android

1. Install "OpenVPN Connect" from App Store / Play Store
2. Transfer `.ovpn` file (AirDrop, email, or cloud)
3. Open file → Import to OpenVPN Connect
4. Tap to connect

### Linux

```bash
# Ubuntu/Debian
sudo apt install openvpn

# Fedora/RHEL
sudo dnf install openvpn

# Connect
sudo openvpn --config client.ovpn
```

## Step 6: Verify Connection

```bash
# Check your public IP (should show VPN server IP)
curl ifconfig.me

# Or check via browser
# Visit: https://whatismyipaddress.com
```

## Quick Commands

```bash
# SSH to server
gcloud compute ssh proxy-server --zone=asia-east1-b

# Check VM status
gcloud compute instances describe proxy-server --zone=asia-east1-b --format="get(status,networkInterfaces[0].accessConfigs[0].natIP)"

# Start/Stop VM (to save costs)
gcloud compute instances stop proxy-server --zone=asia-east1-b
gcloud compute instances start proxy-server --zone=asia-east1-b

# Add new client
sudo ./openvpn-install.sh  # Select "Add a new client"

# Delete VM when done
gcloud compute instances delete proxy-server --zone=asia-east1-b
```

## Notes

- **Cost**: e2-micro is free tier eligible (1 per month)
- **Region**: asia-east1 (Taiwan) has low latency to China
- **Security**: Keep your .ovpn file secure - it contains your VPN credentials
- **Troubleshooting**: Check `sudo systemctl status openvpn-server@server`
