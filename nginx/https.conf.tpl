server {
    listen 80;
    listen [::]:80;
    server_name ${NGINX_SERVER_NAME};

    client_max_body_size ${NGINX_CLIENT_MAX_BODY_SIZE};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        default_type "text/plain";
        try_files $uri =404;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${NGINX_SERVER_NAME};

    client_max_body_size ${NGINX_CLIENT_MAX_BODY_SIZE};

    ssl_certificate /etc/letsencrypt/live/${NGINX_SERVER_NAME}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${NGINX_SERVER_NAME}/privkey.pem;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        default_type "text/plain";
        try_files $uri =404;
    }

    location /media/ {
        alias /var/www/media/;
        access_log off;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
        try_files $uri =404;
    }

    location / {
        proxy_pass http://${APP_UPSTREAM_HOST}:${APP_PORT};
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port 443;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
