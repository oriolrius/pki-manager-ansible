# PKI Host Setup Role

Ansible role to setup Ubuntu hosts with certificates from PKI Manager.

## Supported Platforms

- Ubuntu 22.04 (Jammy)
- Ubuntu 24.04 (Noble)

## Features

- Issue multiple certificates per host
- Automatic CN from hostname
- Configurable SANs (DNS names and IP addresses)
- Install CA certificate in system trust store
- PEM and PKCS12 format support
- Proper file permissions (ssl-cert group for keys)
- Handler notifications for service restarts

## Requirements

- PKI Manager API access with OIDC credentials
- An existing CA in PKI Manager

## Role Variables

### Required Variables

```yaml
pki_api_url: "https://pki.example.com/api/v1"
pki_oidc_url: "https://iam.example.com/realms/pki/protocol/openid-connect/token"
pki_client_id: "your-client-id"
pki_client_secret: "your-client-secret"
pki_ca_id: "your-ca-id"
```

### Optional Variables

```yaml
# SSL certificate validation (default: true)
pki_validate_certs: true

# Install CA in system trust store (default: true)
pki_install_ca_trust: true

# Certificate directories (Ubuntu defaults)
pki_cert_dir: "/etc/ssl/certs"
pki_key_dir: "/etc/ssl/private"
pki_ca_trust_dir: "/usr/local/share/ca-certificates"

# Default certificate settings
pki_cert_validity: 365
pki_cert_algorithm: "RSA-2048"
```

### Certificate List

```yaml
pki_certificates:
  - name: "webserver"              # Identifier (default: hostname)
    cn: "server.example.com"       # Common Name (default: FQDN)
    type: "server"                 # server, client, email, code_signing
    dns_names:                     # DNS SANs (default: [FQDN, hostname])
      - "server.example.com"
      - "www.example.com"
    ip_addresses:                  # IP SANs (default: [default_ipv4])
      - "10.0.0.10"
    validity: 365                  # Days (default: pki_cert_validity)
    format: "pem"                  # pem, p12, pfx
    password: "secret"             # Required for p12/pfx
    cert_filename: "web.crt"       # Custom filename
    key_filename: "web.key"        # Custom filename
    owner: "root"                  # File owner
    group: "root"                  # Cert file group
    key_group: "ssl-cert"          # Key file group
    notify:                        # Handlers to trigger
      - restart nginx
```

## Example Playbook

### Basic Usage

```yaml
- name: Setup host certificates
  hosts: webservers
  become: true
  collections:
    - oriolrius.pki_manager

  vars:
    pki_api_url: "https://pki.example.com/api/v1"
    pki_oidc_url: "https://iam.example.com/realms/pki/protocol/openid-connect/token"
    pki_client_id: "{{ lookup('env', 'PKI_CLIENT_ID') }}"
    pki_client_secret: "{{ lookup('env', 'PKI_CLIENT_SECRET') }}"
    pki_ca_id: "my-ca-id"

    pki_certificates:
      - name: "nginx"
        dns_names:
          - "{{ ansible_fqdn }}"
          - "{{ inventory_hostname }}"
        notify:
          - reload nginx

  handlers:
    - name: reload nginx
      ansible.builtin.service:
        name: nginx
        state: reloaded

  roles:
    - pki_host_setup
```

### Multiple Certificates

```yaml
- name: Setup multiple certificates
  hosts: all
  become: true
  collections:
    - oriolrius.pki_manager

  vars:
    pki_api_url: "{{ vault_pki_api_url }}"
    pki_oidc_url: "{{ vault_pki_oidc_url }}"
    pki_client_id: "{{ vault_pki_client_id }}"
    pki_client_secret: "{{ vault_pki_client_secret }}"
    pki_ca_id: "{{ vault_pki_ca_id }}"

    pki_certificates:
      # Web server certificate
      - name: "nginx"
        type: "server"
        dns_names:
          - "web.example.com"
          - "www.example.com"
        notify:
          - reload nginx

      # Internal API certificate
      - name: "api"
        type: "server"
        dns_names:
          - "api.internal.example.com"
        ip_addresses:
          - "10.0.0.50"
        notify:
          - restart api-service

      # Client certificate for mTLS
      - name: "mtls-client"
        type: "client"
        format: "p12"
        password: "{{ vault_mtls_password }}"

  handlers:
    - name: reload nginx
      ansible.builtin.service:
        name: nginx
        state: reloaded

    - name: restart api-service
      ansible.builtin.service:
        name: api-service
        state: restarted

  roles:
    - pki_host_setup
```

### Using Host Variables

```yaml
# group_vars/webservers.yml
pki_certificates:
  - name: "{{ inventory_hostname }}"
    dns_names: "{{ host_dns_names }}"
    ip_addresses: "{{ host_ip_addresses | default([]) }}"
    notify:
      - reload nginx

# host_vars/web1.example.com.yml
host_dns_names:
  - "web1.example.com"
  - "shop.example.com"
host_ip_addresses:
  - "192.168.1.10"
```

## Installed Files

For PEM format certificates:

| File | Location | Permissions |
|------|----------|-------------|
| Certificate | `/etc/ssl/certs/<name>.crt` | 0644 root:root |
| Private Key | `/etc/ssl/private/<name>.key` | 0640 root:ssl-cert |
| CA Chain | `/etc/ssl/certs/<name>-chain.crt` | 0644 root:root |
| Full Chain | `/etc/ssl/certs/<name>-fullchain.crt` | 0644 root:root |

For PKCS12 format:

| File | Location | Permissions |
|------|----------|-------------|
| PKCS12 | `/etc/ssl/private/<name>.p12` | 0640 root:ssl-cert |

## Output Variables

After the role runs, `pki_issued_certificates` contains information about all issued certificates:

```yaml
pki_issued_certificates:
  nginx:
    cert_id: "abc123"
    cn: "web.example.com"
    cert_path: "/etc/ssl/certs/nginx.crt"
    key_path: "/etc/ssl/private/nginx.key"
    chain_path: "/etc/ssl/certs/nginx-chain.crt"
    fullchain_path: "/etc/ssl/certs/nginx-fullchain.crt"
```

## License

MIT

## Author

Oriol Rius - [joor.net](https://joor.net)
