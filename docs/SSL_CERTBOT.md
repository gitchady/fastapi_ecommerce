# Certbot SSL for production

The production stack uses Nginx in front of FastAPI and can obtain certificates from Let's Encrypt with Certbot.

## Required settings

Set these variables in `.env`:

- `NGINX_SERVER_NAME` - your public domain name
- `CERTBOT_EMAIL` - email used for Let's Encrypt notifications
- `NGINX_PORT=80`
- `NGINX_SSL_PORT=443`

## First certificate issue

1. Start the production stack:

   ```bash
   docker compose -f docker-compose.prod.yaml up -d db web nginx certbot-renew
   ```

2. Request the initial certificate:

   ```bash
   docker compose -f docker-compose.prod.yaml --profile certbot run --rm certbot
   ```

3. Reload Nginx so it starts serving HTTPS immediately:

   ```bash
   docker compose -f docker-compose.prod.yaml restart nginx
   ```

## Renewal

`certbot-renew` runs `certbot renew` every 12 hours. Nginx checks certificate changes every `NGINX_CERT_CHECK_INTERVAL` seconds and reloads itself automatically.

## Important

- DNS for `NGINX_SERVER_NAME` must already point to your server.
- Ports `80` and `443` must be open from the internet.
- `YOOKASSA_RETURN_URL` should use `https://`.
