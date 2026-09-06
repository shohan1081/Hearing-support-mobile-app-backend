#!/bin/bash
# ==============================================================================
# Automatic Let's Encrypt SSL Certificate Setup for navriel.app
# Usage: ./init-letsencrypt.sh <your-email@example.com>
# ==============================================================================

set -e

EMAIL="${1}"

if [ -z "$EMAIL" ]; then
    echo "Usage: ./init-letsencrypt.sh <your-email@example.com>"
    exit 1
fi

DOMAINS="navriel.app,api.navriel.app,www.navriel.app"

echo "=== 1. Ensuring Nginx is running on Port 80 for ACME Challenge ==="
docker compose -f docker-compose.prod.yml up -d nginx

echo "=== 2. Requesting Let's Encrypt SSL Certificate for $DOMAINS ==="
docker compose -f docker-compose.prod.yml run --rm --entrypoint "\
    certbot certonly --webroot -w /var/www/certbot \
    -d navriel.app -d api.navriel.app -d www.navriel.app \
    --email $EMAIL --agree-tos --no-eff-email --force-renewal" certbot

echo "=== 3. Activating HTTPS SSL Nginx Configuration ==="
cp nginx/ssl_navriel.conf nginx/default.conf

echo "=== 4. Reloading Nginx with SSL ==="
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload

echo "=== 5. Starting Background Certbot Auto-Renewal Service ==="
docker compose -f docker-compose.prod.yml up -d certbot

echo "SUCCESS! navriel.app, api.navriel.app, and www.navriel.app are now live on HTTPS!"
