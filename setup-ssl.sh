#!/bin/bash
# setup-ssl.sh — Install Certbot and get SSL certificate for the API domain
# Run this ONCE on your Hostinger VPS as root

set -e

DOMAIN="api-quant.indonesiastockanalyst.my.id"

echo "=== Installing Certbot ==="
apt-get update -y
apt-get install -y certbot

echo "=== Stopping any service on port 80 temporarily ==="
# Stop nginx/docker if running so certbot can use port 80
docker compose down 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true

echo "=== Obtaining SSL certificate for $DOMAIN ==="
certbot certonly --standalone \
  --non-interactive \
  --agree-tos \
  --email admin@indonesiastockanalyst.my.id \
  -d "$DOMAIN"

echo "=== Certificate obtained! ==="
echo "Cert path: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
echo "Key path:  /etc/letsencrypt/live/$DOMAIN/privkey.pem"

echo "=== Setting up auto-renewal ==="
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --pre-hook 'docker compose -f /root/prediksi-saham-LQ45/docker-compose.yml down' --post-hook 'docker compose -f /root/prediksi-saham-LQ45/docker-compose.yml up -d'") | crontab -

echo "=== Starting services back up ==="
cd "$(dirname "$0")"
docker compose up -d --build

echo ""
echo "=== DONE ==="
echo "Test your API: curl https://$DOMAIN/health"
