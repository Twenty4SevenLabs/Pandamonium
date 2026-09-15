# Plan: Pandamonium prod-only hosting

1. On `vm-gpu-creative` (M1 guest): `tailscale serve --https=7080 off`; `systemctl disable --now pandamonium.service pandamonium-lan-forward.service`. Leave Chatterbox, Unsloth, `:7088`.
2. On pve-heavy: `systemctl disable pandamonium.service` (already inactive).
3. Delete `docker/host-m1-heavy.yml`; restore `deploy/systemd/pandamonium.service` to pve-prod compose files only.
4. Strip `m1:7080` and `192.168.1.2:7080` from `.env` `ALLOWED_ORIGINS`. Recreate the prod container.
5. Update `/mnt/dev-env/MAP.md`. Verify prod `:7080` healthy, M1 `:7080` gone, Chatterbox `:8030` still listening.
