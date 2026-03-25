#!/bin/sh
set -eu

state_file="/tmp/nginx-cert-state"
interval="${NGINX_CERT_CHECK_INTERVAL:-300}"

get_state() {
    cert_dir="/etc/letsencrypt/live/${NGINX_SERVER_NAME}"
    fullchain="${cert_dir}/fullchain.pem"
    privkey="${cert_dir}/privkey.pem"

    if [ -f "$fullchain" ] && [ -f "$privkey" ]; then
        checksum="$(sha256sum "$fullchain" "$privkey" | sha256sum | awk '{print $1}')"
        printf 'https:%s\n' "$checksum"
        return
    fi

    printf 'http:no-cert\n'
}

(
    printf '%s\n' "$(get_state)" > "$state_file"

    while :; do
        sleep "$interval"

        current_state="$(get_state)"
        previous_state="$(cat "$state_file" 2>/dev/null || printf '')"

        if [ "$current_state" != "$previous_state" ]; then
            /usr/local/bin/render-nginx-config.sh
            if nginx -t; then
                nginx -s reload || true
                printf '%s\n' "$current_state" > "$state_file"
            fi
        fi
    done
) &
