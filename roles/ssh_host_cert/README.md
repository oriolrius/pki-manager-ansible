# `ssh_host_cert` role

Provision a **full SSH-CA node** from the PKI Manager REST API in one run. The
host key is generated **on the node** (the private key never leaves it); only
the public key is signed. Every API call goes through the collection's
`pki_manager` module (REST, no `curl`, no tRPC).

What one run does: generate the host key → `ssh_sign_host` + install the cert →
install the **User-CA** and **Host-CA** trust anchors → populate
`/etc/ssh/auth_principals/<account>` (login RBAC) + a fail-closed `RevokedKeys`
placeholder → install the authoritative, algorithm-aware sshd drop-in
(`ssh_sshd_config`) → `sshd -t` + reload → install unattended renewal →
*(ECIES)* register the ecdsa key + install the `krl-client` puller.

## Requirements

- `community.crypto` (declared as a collection dependency).
- A fleet token scoped to the Host CA with ops `sign-host`, `get-principals`,
  and — for ECIES — `register-host-pubkey`. Mint it with
  `pki_manager: action=ssh_token_mint` (see the collection README).
- Backend: `SSH_ECIES_ENABLED=true` for the encrypted-KRL channel; with OIDC
  off, `ALLOW_UNAUTHENTICATED_SSH_CA=true`.
- NTP/chrony on every host (cert validity + KRL freshness depend on it; enforced
  on the ECIES path).

## Key variables (`defaults/main.yml`)

| Variable | Default | Meaning |
|---|---|---|
| `ssh_ca_base_url` | `https://pki.internal` | PKI Manager base URL |
| `ssh_ca_fleet_token` | `""` | fleet bearer token (**vault this**) |
| `ssh_host_cert_ecies_enabled` | `false` | ecdsa host key + register + `krl-client` puller |
| `ssh_host_cert_krl_client_url` | `""` | `krl-client` binary source (https or `file:///`) |
| `ssh_host_cert_krl_client_checksum` | `""` | `sha256:…` (idempotence + tamper guard) |
| `ssh_host_cert_renew_enabled` | `true` | unattended host-cert renewal (cron/systemd) |
| `ssh_host_cert_scheduler` | `cron` | `cron` (portable) or `systemd` (timers) |
| `ssh_host_cert_reload_method` | `service` | `service`, or `command` (SIGHUP, init-less containers) |
| `ssh_host_cert_known_hosts_enabled` | `false` | install `@cert-authority` client-trust line |
| `ssh_host_cert_x509_*` | `false` | X.509 CA-trust + CRL stretch (non-SSH) |

See `defaults/main.yml` for the full set (principals prune, renewal cadence,
`krl-client` config/state paths, TLS ca-bundle, per-host public-KRL cron).

## Usage

Run it inside the end-to-end example
([`examples/ssh_deploy_server_and_user.yml`](../../examples/ssh_deploy_server_and_user.yml)),
or standalone:

```yaml
- hosts: sshservers
  become: true
  gather_facts: true   # needs ansible_fqdn + ansible_all_ipv4_addresses
  vars:
    ssh_ca_base_url: https://pki.example.com
    ssh_ca_fleet_token: "{{ vault_fleet_token }}"
    ssh_host_cert_ecies_enabled: true
    ssh_host_cert_krl_client_url: https://artifacts.example.com/krl-client-linux-amd64
    ssh_host_cert_krl_client_checksum: "sha256:<hex>"
  roles:
    - oriolrius.pki_manager.ssh_host_cert
```
