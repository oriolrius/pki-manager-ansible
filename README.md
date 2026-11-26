# PKI Manager Ansible Collection

**`oriolrius.pki_manager`** — an Ansible collection for managing **both X.509 certificates and the SSH certificate workflow** through the PKI Manager REST API (one module plus two host-setup roles).

- **Version:** 3.0.0 (tested against PKI Manager 3.19.0)
- **Collection (FQCN):** `oriolrius.pki_manager`
- **Requires:** Ansible `>=2.14.0`, `community.crypto >=2.0.0`
- **Repository:** https://github.com/oriolrius/pki-manager-ansible

---

## Features

The collection covers two co-equal certificate domains through a single `pki_manager` module plus dedicated roles. All API calls are REST — no `curl`, no tRPC.

### X.509 certificates

- **CA lifecycle** — create, list, get, revoke, delete Certificate Authorities.
- **Certificate lifecycle** — issue, list, get, renew, revoke, delete leaf certificates (`server`, `client`, `dual`, `email`, `code_signing`).
- **Downloads** — export in 15 formats (PEM/DER, chain/full, key, CSR, PKCS#8, PKCS#12/PFX, JKS keystore/truststore).
- **Search & dashboards** — search across CAs and certificates, PKI statistics, soon-expiring monitoring.
- **`pki_host_setup` role** — provision Ubuntu hosts with issued X.509 certs installed to standard locations, with handler notifications.

### SSH certificate authority

- **SSH CAs** — create and list user/host SSH CAs.
- **Fleet tokens** — mint scoped `pkimg_…` bearer tokens for host-facing operations.
- **Identities, principals & host maps** — create identities, define principals, grant entitlements, and map principals to local accounts (login RBAC).
- **User certificates** — issue SSH user certs against granted principals.
- **Host certificates** — register host pubkeys, sign host certs, and (ECIES) register encrypted-KRL host keys — the private host key never leaves the node.
- **Trust anchors & renders** — fetch `@cert-authority` lines, `TrustedUserCAKeys`/host-CA anchors, and render authoritative `auth_principals` / sshd drop-in files.
- **Access blocks** — block/unblock an identity on a host.
- **`ssh_host_cert` role** — turn a node into a full SSH-CA client: host key generation, cert install, trust anchors, login-RBAC principals, authoritative sshd drop-in, unattended renewal, and KRL revocation.

### Shared

- **OIDC authentication is optional** with automatic token caching — omit OIDC entirely for a backend running with `ALLOW_UNAUTHENTICATED_SSH_CA=true`, or use a fleet token for host-facing SSH actions.
- **Check mode** — every state-changing action short-circuits to a `would …(check mode)` message; read-only actions run normally.

---

## Components

| Component | Type | Purpose |
|---|---|---|
| `oriolrius.pki_manager.pki_manager` | Module | Full REST access to all 36 actions — 16 X.509 + 20 SSH. |
| `oriolrius.pki_manager.pki_host_setup` | Role | Issue and install X.509 host certificates on Ubuntu. |
| `oriolrius.pki_manager.ssh_host_cert` | Role | Provision a full SSH-CA node (host cert, trust anchors, principals, sshd drop-in, renewal, KRL). |

Both roles target **Ubuntu 22.04 (jammy)** and **Ubuntu 24.04 (noble)** only.

---

## Installation

### From Ansible Galaxy

```bash
ansible-galaxy collection install oriolrius.pki_manager
```

### Using requirements.yml

```yaml
# requirements.yml
collections:
  - name: oriolrius.pki_manager
    version: ">=3.0.0"
```

```bash
ansible-galaxy collection install -r requirements.yml
```

The `community.crypto >=2.0.0` dependency is resolved automatically from the collection's `galaxy.yml`.

### From GitHub

```bash
ansible-galaxy collection install git+https://github.com/oriolrius/pki-manager-ansible.git,v3.0.0
```

---

## Quick start

Two peer workflows — pick your domain.

### X.509 — create a CA and issue a server certificate

```yaml
- hosts: localhost
  gather_facts: false
  collections: [oriolrius.pki_manager]
  vars:
    api_url: "https://pki.example.com/api/v1"
    oidc_url: "https://iam.example.com/realms/pki/protocol/openid-connect/token"
    client_id: "{{ lookup('env', 'PKI_CLIENT_ID') }}"
    client_secret: "{{ lookup('env', 'PKI_CLIENT_SECRET') }}"
  tasks:
    - name: Create a Root CA
      pki_manager:
        action: ca_create
        api_url: "{{ api_url }}"
        oidc_url: "{{ oidc_url }}"
        client_id: "{{ client_id }}"
        client_secret: "{{ client_secret }}"
        ca_cn: "My Root CA"
        ca_org: "My Organization"
        ca_country: "US"
      register: ca

    - name: Issue a server certificate
      pki_manager:
        action: cert_issue
        api_url: "{{ api_url }}"
        oidc_url: "{{ oidc_url }}"
        client_id: "{{ client_id }}"
        client_secret: "{{ client_secret }}"
        ca_id: "{{ ca.ca_id }}"
        cert_cn: "webserver.example.com"
        cert_org: "My Organization"
        cert_country: "US"
        cert_type: "server"
        cert_dns_names: ["webserver.example.com", "www.example.com"]
      register: cert
```

### SSH — deploy a server and onboard a user

Full runnable playbook: [`examples/ssh_deploy_server_and_user.yml`](examples/ssh_deploy_server_and_user.yml). It creates a User/Host CA, mints a fleet token, defines a `developers` principal, provisions hosts into full SSH-CA nodes via the `ssh_host_cert` role (ECIES channel), then onboards user `alice` (identity → grant → principal→account map → user cert → client `ssh_config`/`known_hosts` with `@cert-authority` trust).

```yaml
- hosts: localhost
  gather_facts: false
  collections: [oriolrius.pki_manager]
  tasks:
    - name: Create the Host CA
      pki_manager:
        action: ssh_ca_create
        api_url: "https://pki.example.com/api/v1"
        ssh_ca_type: host
      register: host_ca

    - name: Mint a fleet token for the servers
      pki_manager:
        action: ssh_token_mint
        api_url: "https://pki.example.com/api/v1"
        token_name: acme-fleet
        host_ca_id: "{{ host_ca.ca_id }}"
        token_ops: [sign-host, get-principals, register-host-pubkey]
      register: fleet
    # ...then apply the ssh_host_cert role to your `sshservers` group.
```

---

## Module actions

The single `pki_manager` module exposes 36 actions — 16 X.509 + 20 SSH.

### X.509 actions

| Action | Purpose | Key parameters |
|---|---|---|
| `auth_test` | Test auth / `GET /health` | — |
| `stats` | Get PKI dashboard statistics | — |
| `expiring` | List soon-expiring certificates | `expiring_limit` |
| `search` | Search CAs and certificates | `search_query`, `search_limit` |
| `ca_create` | Create a Certificate Authority | `ca_cn`, `ca_org`, `ca_country` |
| `ca_list` | List Certificate Authorities | — |
| `ca_get` | Get CA details | `ca_id` |
| `ca_revoke` | Revoke a CA | `ca_id`, `revocation_reason` |
| `ca_delete` | Delete a CA | `ca_id` |
| `cert_issue` | Issue a leaf certificate | `ca_id`, `cert_cn` |
| `cert_list` | List certificates | — |
| `cert_get` | Get certificate details | `cert_id` |
| `cert_renew` | Renew a certificate | `cert_id` |
| `cert_revoke` | Revoke a certificate | `cert_id`, `revocation_reason` |
| `cert_delete` | Delete a certificate | `cert_id` |
| `cert_download` | Download certificate in a format | `cert_id`, `download_format`, `download_password`, `download_dest` |

### SSH actions

| Action | Purpose | Key parameters |
|---|---|---|
| `ssh_ca_create` | Create SSH user/host CA | `ssh_ca_type`, `ssh_ca_label` |
| `ssh_ca_list` | List SSH CAs | — |
| `ssh_token_mint` | Mint fleet bearer token | `token_name`, `token_ops`, `host_ca_id`/`user_ca_id` |
| `ssh_identity_create` | Create SSH identity | `identity_subject`, `identity_email` |
| `ssh_principal_create` | Create SSH principal | `principal_name`, `principal_description` |
| `ssh_principal_grant` | Grant principal to identity | `identity_id`, `principal_id` |
| `ssh_principal_map` | Map principal to local account | `host_id`, `principal_id`, `local_account` |
| `ssh_user_issue` | Issue SSH user certificate | `identity_id`, `ssh_public_key`, `principals`, `user_valid_seconds` |
| `ssh_host_register` | Register SSH host pubkey | `host_fqdn`, `host_pubkey`, `host_addresses` |
| `ssh_host_list` | List / resolve SSH hosts | `host_fqdn` |
| `ssh_block` | Block identity on host | `host_id`, `identity_id`, `block_reason` |
| `ssh_unblock` | Unblock identity on host | `host_id`, `identity_id` |
| `ssh_auth_principals` | Render host `auth_principals` file | `host_id` |
| `ssh_sshd_config` | Render sshd drop-in config | `host_id` |
| `ssh_cert_authority` | Fetch `@cert-authority` known_hosts line | `cert_authority_pattern` |
| `ssh_trusted_user_ca` | Fetch `TrustedUserCAKeys` content | — |
| `ssh_host_ca` | Fetch host-CA trust anchor | — |
| `ssh_sign_host` | Sign host cert (fleet-token) | `host_fqdn`, `host_pubkey`, `fleet_token`, `host_valid_seconds`, `host_key_id`, `idempotency_key` |
| `ssh_register_host_pubkey` | Register ECIES host key (fleet-token) | `host_fqdn`, `fleet_token` |
| `ssh_get_principals` | Fetch host `auth_principals` (fleet-token) | `host_fqdn`, `fleet_token` |
| `ssh_principals_pushed` | Acknowledge the installed principal files so the host is not Stale (fleet-token; 409 `SHA256_MISMATCH` fails with `sha256_mismatch`/`current_sha256`; no-op in check mode) | `host_fqdn`, `fleet_token`, `principals_sha256` |

X.509 and SSH-admin actions hit `{api_url}/…` with the optional OIDC Bearer. Host-facing actions (`ssh_sign_host`, `ssh_register_host_pubkey`, `ssh_get_principals`, `ssh_principals_pushed`) hit `/external/ssh` with the `fleet_token` Bearer. `required_if` enforces per-action mandatory parameters (e.g. `ssh_sign_host` requires `host_fqdn` + `host_pubkey` + `fleet_token`).

---

## Key parameters

### Connection / OIDC (OIDC optional)

| Parameter | Required | Default | Description |
|---|---|---|---|
| `action` | Yes | — | Action to perform (see tables above) |
| `api_url` | Yes | — | PKI Manager REST base URL |
| `oidc_url` | No | — | OIDC token endpoint (omit when OIDC is disabled) |
| `client_id` | No | — | OIDC client ID |
| `client_secret` | No | — | OIDC client secret (`no_log`) |
| `api_token` | No | — | A bearer token you got before (`no_log`); the module then skips the OIDC login |
| `validate_certs` | No | `true` | Verify the PKI Manager TLS certificate |
| `ca_path` | No | — | PEM bundle to trust a server with a private CA (use it instead of `validate_certs: false`) |
| `timeout` | No | `30` | Request timeout (seconds) |
| `token_cache_path` | No | `~/.cache/pki-manager-ansible/token-<hash>.json` | OIDC token cache. The default name comes from `api_url`, `oidc_url` and `client_id`, so two servers or clients never share a token. The file is mode 0600 in a 0700 directory; the module ignores a cache file that another user owns, that others can read, or that was written for another server or client. A cached token that the server refuses (401) is dropped and the module logs in again once. |
| `fleet_token` | No | — | `pkimg_…` bearer (`no_log`) for host-facing SSH actions |

When `api_token` and `oidc_url`/`client_id`/`client_secret` are absent, the module sends unauthenticated requests — suitable for a backend with OIDC disabled. `auth_test` calls an endpoint that needs authentication, so it fails on a bad token.

### Per-domain parameters

- **X.509 CA** — `ca_id`, `ca_cn`/`ca_org`/`ca_country` (required for `ca_create`), optional `ca_ou`/`ca_state`/`ca_locality`, `ca_algorithm` (`RSA-2048|RSA-4096`, default `RSA-4096`; the API takes only RSA for a CA), `ca_validity_years` (1-30; server default 20). `ca_validity` (days) is deprecated: the module rounds it to years.
- **X.509 certificate** — `cert_id`, `cert_cn`, `cert_org` and `cert_country` (required for `cert_issue`), optional `cert_ou`/`cert_state`/`cert_locality`, `cert_type` (default `server` for `cert_issue`; a filter for `cert_list`), `cert_status` (filter for `cert_list`), `cert_algorithm` (default `RSA-2048`), `cert_validity` (days, default `365`), SAN lists `cert_dns_names`/`cert_ip_addresses`/`cert_emails`.
- **Downloads** — `download_format` (default `pem`): `pem`, `der`, `chain-pem`, `full-pem`, `full-der`, `key-pem`, `key-der`, `csr-pem`, `p12`, `pfx`, `pkcs8-pem`, `pkcs8-der`, `pkcs8-encrypted`, `jks-keystore`, `jks-truststore`. `download_password` is required for `p12`/`pfx`/`jks-keystore`/`jks-truststore`/`pkcs8-encrypted`. The password goes in the `X-Export-Password` header, never in the URL. `download_dest` is written `chmod 0600`; if omitted, content is returned base64-encoded. The REST `chain-pem` format returns only the certificate (server bug); `full-pem` has the certificate and the CA.
- **Revocation** — `revocation_reason` (shared by `ca_revoke` and `cert_revoke`): `unspecified` (default), `keyCompromise`, `caCompromise`, `affiliationChanged`, `superseded`, `cessationOfOperation`, `certificateHold`, `removeFromCRL`.
- **Lists** — `ca_list` and `cert_list` read every page, so `cas`/`certificates` hold all items (not only the first 50).
- **Search / dashboards** — `search_query` (required for `search`), `search_limit` (default `10`), `expiring_limit` (default `5`, capped at `20`).
- **SSH** — `ssh_ca_type` (`user|host`), `ssh_ca_label`; `token_name`, `token_ops` (e.g. `sign-host`/`get-principals`/`register-host-pubkey`), `host_ca_id`/`user_ca_id`; `identity_id`/`identity_subject`/`identity_email`/`identity_external_subject`; `principal_id`/`principal_name`/`principal_description`; `host_id`/`host_fqdn`/`host_pubkey`/`host_addresses`/`local_account`; `ssh_public_key`, `principals`, `user_valid_seconds` (`validForSeconds` of `ssh_user_issue`), `host_valid_seconds` and `host_key_id` (`ssh_sign_host`; `user_valid_seconds` is still accepted there when `host_valid_seconds` is not set), `enforce_entitlement`; `cert_authority_pattern` (default `*`), `block_reason`, `idempotency_key` (`Idempotency-Key` header for `ssh_sign_host`).

---

## Roles

### `pki_host_setup` — X.509 host certificates

Provisions Ubuntu hosts with X.509 certificates issued from the PKI Manager REST API. All API calls run on the controller (`delegate_to: localhost`), so the OIDC secret and tokens never reach the managed hosts. The role is idempotent: a state file per certificate (`pki_state_dir`) records the certificate id, a hash of the request and `notAfter`, and a new certificate is issued only when the request changes, a file is missing, the certificate expires within `pki_cert_renew_before_days` (default 30), or `force: true` is set. The replaced certificate is revoked (`superseded`) unless `pki_revoke_replaced: false`. It issues one or more certs from a chosen CA (CN auto-derived from the hostname/FQDN, configurable DNS+IP SANs, per-cert type/validity/format), installs them to standard Ubuntu locations with correct permissions (certs `0644 root:root`, keys `0640 root:ssl-cert`), optionally installs the CA into the system trust store, supports PEM and PKCS12/PFX output, and fires handler notifications (e.g. reload nginx) on change. Exports `pki_issued_certificates` with per-cert id/CN/paths.

| Variable | Default | Notes |
|---|---|---|
| `pki_api_url` | `""` | **Required** — REST base, e.g. `https://pki.example.com/api/v1` |
| `pki_oidc_url` | `""` | OIDC token endpoint (with `pki_client_id` / `pki_client_secret`) |
| `pki_client_id` / `pki_client_secret` | `""` | OIDC credentials — set these three, or `pki_api_token` |
| `pki_api_token` | `""` | A bearer token you got before, instead of the OIDC credentials |
| `pki_ca_path` | `""` | PEM bundle on the controller to trust a private-CA server |
| `pki_ca_id` | `""` | **Required** — issuing CA id |
| `pki_certificates` | `[]` | Certs to issue/install (`name`, `cn`, `type`, `dns_names`, `ip_addresses`, `validity`, `format`, `password`, `*_filename`, `owner`, `group`, `key_group`, `notify`) |
| `pki_cert_org` / `pki_cert_country` | `""` | Subject O and C (2-letter); required by API |
| `pki_validate_certs` | `true` | Verify PKI Manager TLS cert |
| `pki_install_ca_trust` | `true` | Install CA into `/usr/local/share/ca-certificates` |
| `pki_cert_dir` / `pki_key_dir` / `pki_ca_trust_dir` | `/etc/ssl/certs` / `/etc/ssl/private` / `/usr/local/share/ca-certificates` | Install locations |
| `pki_cert_validity` / `pki_cert_algorithm` | `365` / `RSA-2048` | Default lifetime / key algorithm |
| `pki_state_dir` | `/etc/pki-manager/certs` | One state file per certificate (idempotency) |
| `pki_cert_renew_before_days` | `30` | Issue a new certificate when the installed one expires sooner |
| `pki_cert_force` | `false` | Issue again on every run (or `force: true` on one entry) |
| `pki_revoke_replaced` | `true` | Revoke (`superseded`) the certificate a new one replaces |

The default DNS SANs are `ansible_fqdn` and `ansible_hostname`, but only the names with two or more labels: the API rejects `web`. A host with no FQDN must set `cn` (and `dns_names`) for a `server` or `dual` certificate. The chain file is the CA certificate.

Full docs: [`roles/pki_host_setup/README.md`](roles/pki_host_setup/README.md).

### `ssh_host_cert` — full SSH-CA node

Provisions a full SSH-CA node from the PKI Manager external REST API in a single run. The host key is generated **on** the node (the private key never leaves it); only the public key is signed via `POST /api/v1/external/ssh/sign-host` using a fleet bearer token. One run generates the host key, signs and installs the cert, installs the User-CA and Host-CA trust anchors, populates `/etc/ssh/auth_principals/<account>` for login RBAC plus a fail-closed `RevokedKeys` placeholder, installs the authoritative algorithm-aware sshd drop-in (`60-ssh-ca.conf`), runs `sshd -t` and reloads, installs unattended host-cert renewal, and — on the ECIES path — registers the ecdsa key and installs the `krl-client` puller. All API calls go through the `pki_manager` module (REST only).

| Variable | Default | Notes |
|---|---|---|
| `ssh_ca_base_url` | `https://pki.internal` | PKI Manager base URL |
| `ssh_ca_fleet_token` | `""` | **Must be vaulted** — `pkimg_…` token scoped to one Host CA (ops `sign-host`, `get-principals`, and ECIES `register-host-pubkey`) |
| `ssh_host_cert_ecies_enabled` | `false` | Master switch for the encrypted-KRL path (forces an `ecdsa-sha2-nistp256` host key) |
| `ssh_host_cert_key_type` | `ecdsa` | Host key algorithm: the backend accepts only `ecdsa-sha2-nistp256` host keys |
| `ssh_host_cert_renew_enabled` | `true` | Unattended renewal (stores the fleet token `0600` on the host) |
| `ssh_host_cert_scheduler` | `cron` (alt `systemd`) | Substrate for renewal + krl-client |
| `ssh_host_cert_reload_method` | `service` (alt `command` = SIGHUP) | How sshd reload runs |
| `ssh_host_cert_principals_enabled` / `_prune` | `true` / `false` | Populate / prune `AuthorizedPrincipalsFile` |
| `ssh_host_cert_krl_client_url` / `_checksum` | `""` / `""` | krl-client binary source + `sha256:…` guard |
| `ssh_host_cert_krl_cron_enabled` | `false` | Public-path KRL refresh cron (non-ECIES hosts) |
| `ssh_host_cert_known_hosts_enabled` | `false` | Install `@cert-authority` client-trust line |
| `ssh_host_cert_x509_ca_trust_enabled` / `_x509_crl_cron_enabled` | `false` | Optional non-SSH X.509 CA-trust + CRL refresh |
| `ssh_host_cert_renew_bucket_format` | `%G-%V` | ISO year-week (re-mints a fresh 52-week cert weekly) |
| `ssh_host_cert_renew_cron` / `_renew_oncalendar` | `17 3 * * *` / `*-*-* 03:17:00` | Renewal schedule (cron / systemd) |
| `ssh_host_cert_krl_client_interval_minutes` | `15` | krl-client poll interval |
| `ssh_host_cert_require_timesync` | `true` | NTP/chrony is a hard prereq (krl-client exits 5 on clock drift) |

Full docs: [`roles/ssh_host_cert/README.md`](roles/ssh_host_cert/README.md).

---

## Examples

| File | What it shows |
|---|---|
| [`examples/webserver_setup.yml`](examples/webserver_setup.yml) | `pki_host_setup` provisioning multiple TLS server certs (nginx-main, nginx-api) with DNS/IP SANs, reload-nginx handlers, and SSL config rendered from the issued paths. |
| [`examples/ssh_deploy_server_and_user.yml`](examples/ssh_deploy_server_and_user.yml) | End-to-end SSH workflow (no `curl`): dual User/Host CA, fleet-token mint, `developers` principal, `ssh_host_cert` role over ECIES, then onboarding user `alice` (identity, grant, principal→account map, user cert, client `ssh_config`/`known_hosts` with `@cert-authority` trust). |

## Tests

```bash
export PKI_API_URL="https://pki.example.com/api/v1"
export PKI_OIDC_URL="https://iam.example.com/realms/pki/protocol/openid-connect/token"
export PKI_CLIENT_ID="your-client-id"
export PKI_CLIENT_SECRET="your-client-secret"

ansible-galaxy collection build
ansible-galaxy collection install oriolrius-pki_manager-*.tar.gz --force

ansible-playbook tests/test_module.yml       # X.509 CRUD/lifecycle smoke test
ansible-playbook tests/test_ssh_module.yml   # every SSH action (unauthenticated + ECIES)
ansible-playbook tests/test_role.yml         # pki_host_setup integration
ansible-playbook tests/test_role_syntax.yml  # offline --check structural validation
```

---

## Supported platforms

Both roles target **Ubuntu only**: Ubuntu 22.04 (jammy) and Ubuntu 24.04 (noble). Minimum Ansible `2.14`.

---

## Authentication

The collection supports three modes:

- **OIDC (optional)** — set `oidc_url` + `client_id` + `client_secret` for client-credentials auth; tokens are cached at `token_cache_path` (`0600`, 60 s buffer).
- **Unauthenticated** — omit OIDC entirely against a backend started with `ALLOW_UNAUTHENTICATED_SSH_CA=true`.
- **Fleet token** — host-facing SSH actions (`ssh_sign_host`, `ssh_register_host_pubkey`, `ssh_get_principals`, `ssh_principals_pushed`) use a `pkimg_…` `fleet_token` bearer against `/external/ssh`.

**Backend prerequisites for SSH:** `SSH_ECIES_ENABLED=true` (encrypted-KRL channel), `ALLOW_UNAUTHENTICATED_SSH_CA=true` (when OIDC is off), `SSH_HOST_KRL_PUBLIC=true` (per-host public KRL blocks), and NTP/chrony on every host.

---

## Related projects

| Project | Description |
|---|---|
| [PKI Manager](https://github.com/oriolrius/pki-manager-web) | Main PKI Manager web application |
| [PKI Manager CLI](https://github.com/oriolrius/pki-manager-cli) | CLI for PKI Manager (`pki`, one static binary for Linux, Windows and macOS) |
| [PKI Manager Skill](https://github.com/oriolrius/pki-manager-skill) | Claude Code skill for AI-assisted certificate management |

---

## License

MIT — Oriol Rius <oriol@joor.net> ([joor.net](https://joor.net)).