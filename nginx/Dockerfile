FROM nginx:1.27-alpine

COPY http-only.conf.tpl /etc/nginx/custom-templates/http-only.conf.tpl
COPY https.conf.tpl /etc/nginx/custom-templates/https.conf.tpl
COPY render-nginx-config.sh /usr/local/bin/render-nginx-config.sh
COPY 10-render-config.sh /docker-entrypoint.d/10-render-config.sh
COPY 20-watch-certificates.sh /docker-entrypoint.d/20-watch-certificates.sh

RUN chmod +x /usr/local/bin/render-nginx-config.sh \
    /docker-entrypoint.d/10-render-config.sh \
    /docker-entrypoint.d/20-watch-certificates.sh

EXPOSE 80 443
