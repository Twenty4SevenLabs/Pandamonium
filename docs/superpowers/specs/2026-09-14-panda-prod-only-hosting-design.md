# Pandamonium hosts on prod only

Date: 2026-09-14  
Status: locked

## Decision

Pandamonium’s UI is served only from pve-prod (`https://prod.tail61d527.ts.net:7080`). Linux M1 (`vm-gpu-creative` / `m1.tail61d527.ts.net`) must not serve Pandamonium on `:7080`. Chatterbox TTS on M1 `:8030` and the Unsloth Studio fleet (including M1 `:8888`) stay.

## Keep on M1

- Chatterbox `http://192.168.1.181:8030/v1`
- Unsloth Studio `:8888` and Tailscale Serve HTTPS `/` → loopback `:8888`
- Superpowers preview `:7088` (not Pandamonium)

## Remove

- Tailscale Serve `https://m1.tail61d527.ts.net:7080`
- Native `pandamonium.service` and `pandamonium-lan-forward.service` on `vm-gpu-creative`
- Enabled-but-idle Docker `pandamonium.service` on pve-heavy
- `docker/host-m1-heavy.yml` and systemd compose overlay that binds `192.168.1.2:7080`
- `ALLOWED_ORIGINS` entries for `m1:7080` and `http://192.168.1.2:7080`

## Public origin

`APP_PUBLIC_URL` / OAuth / CORS: `https://prod.tail61d527.ts.net:7080` (plus local `127.0.0.1:7080` and `prod-1` if still used).
