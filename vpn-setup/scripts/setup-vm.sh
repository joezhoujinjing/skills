#!/bin/bash
# Quick GCP VM setup for OpenVPN

set -e

VM_NAME="${1:-proxy-server}"
ZONE="${2:-asia-east1-b}"

echo "Creating VM: $VM_NAME in $ZONE..."

# Create VM
gcloud compute instances create "$VM_NAME" \
  --zone="$ZONE" \
  --machine-type=e2-micro \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=10GB \
  --tags=https-server \
  --metadata=enable-oslogin=true

# Create firewall rules (ignore if exists)
gcloud compute firewall-rules create allow-openvpn \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=udp:1194 \
  --source-ranges=0.0.0.0/0 \
  --description="Allow OpenVPN traffic" 2>/dev/null || true

echo ""
echo "VM created! Next steps:"
echo "  1. SSH: gcloud compute ssh $VM_NAME --zone=$ZONE"
echo "  2. Install OpenVPN: curl -O https://raw.githubusercontent.com/angristan/openvpn-install/master/openvpn-install.sh && chmod +x openvpn-install.sh && sudo ./openvpn-install.sh"
echo "  3. Download config: gcloud compute scp $VM_NAME:~/CLIENT.ovpn . --zone=$ZONE"
