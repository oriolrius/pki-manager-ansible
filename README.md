# PKI Manager Ansible Collection

Ansible collection for managing X.509 certificates via PKI Manager API.

## Features

- **Module (`pki_manager`)**: Full API access for CA and certificate operations
- **Role (`pki_host_setup`)**: Automated host certificate provisioning for Ubuntu
- OIDC authentication with automatic token caching
- CA management (create, list, get, revoke, delete)
- Certificate management (issue, list, get, renew, revoke, delete)
- Certificate download in multiple formats (PEM, DER, P12, JKS, etc.)
- Search across CAs and certificates
- Statistics and expiring certificates monitoring
- Check mode support

## Supported Platforms (Role)

- Ubuntu 22.04 (Jammy)
- Ubuntu 24.04 (Noble)

## Installation

### From Ansible Galaxy

```bash
ansible-galaxy collection install oriolrius.pki_manager
```

### From GitHub

```bash
ansible-galaxy collection install git+https://github.com/oriolrius/pki-manager-ansible.git,v1.0.0
```

### Using requirements.yml

```yaml
# requirements.yml
collections:
  - name: oriolrius.pki_manager
    version: ">=1.0.0"
```

```bash
ansible-galaxy collection install -r requirements.yml
```

## Quick Start

```yaml
- name: PKI Operations
  hosts: localhost
  collections:
    - oriolrius.pki_manager
  vars:
    pki_api_url: "https://pki.example.com/api/v1"
    pki_oidc_url: "https://iam.example.com/realms/pki/protocol/openid-connect/token"
    pki_client_id: "{{ lookup('env', 'PKI_CLIENT_ID') }}"
    pki_client_secret: "{{ lookup('env', 'PKI_CLIENT_SECRET') }}"

  tasks:
    - name: Issue a certificate
      pki_manager:
        action: cert_issue
        api_url: "{{ pki_api_url }}"
        oidc_url: "{{ pki_oidc_url }}"
        client_id: "{{ pki_client_id }}"
        client_secret: "{{ pki_client_secret }}"
        ca_id: "your-ca-id"
        cert_cn: "server.example.com"
        cert_type: "server"
        cert_dns_names:
          - "server.example.com"
          - "www.example.com"
      register: cert_result

    - name: Download certificate
      pki_manager:
        action: cert_download
        api_url: "{{ pki_api_url }}"
        oidc_url: "{{ pki_oidc_url }}"
        client_id: "{{ pki_client_id }}"
        client_secret: "{{ pki_client_secret }}"
        cert_id: "{{ cert_result.cert_id }}"
        download_format: "p12"
        download_password: "{{ vault_password }}"
        download_dest: "/etc/ssl/server.p12"
```

Or using fully qualified collection name (FQCN):

```yaml
- name: Issue a certificate
  oriolrius.pki_manager.pki_manager:
    action: cert_issue
    api_url: "{{ pki_api_url }}"
    # ... other parameters
```

## Host Setup Role

The `pki_host_setup` role automates certificate provisioning for Ubuntu hosts. It issues certificates with the hostname as CN, installs them in standard locations, and optionally notifies services to reload.

### Basic Role Usage

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
    pki_ca_id: "your-ca-id"

    pki_certificates:
      - name: "nginx"
        dns_names:
          - "{{ ansible_fqdn }}"
          - "web.example.com"
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
pki_certificates:
  # Web server certificate
  - name: "nginx"
    type: "server"
    dns_names:
      - "web.example.com"
      - "www.example.com"
    ip_addresses:
      - "10.0.0.10"
    notify:
      - reload nginx

  # API server certificate
  - name: "api"
    type: "server"
    dns_names:
      - "api.example.com"
    notify:
      - restart api

  # Client certificate for mTLS
  - name: "mtls-client"
    type: "client"
    format: "p12"
    password: "{{ vault_password }}"
```

### Certificate Options

| Option | Default | Description |
|--------|---------|-------------|
| `name` | hostname | Certificate identifier |
| `cn` | FQDN | Common Name |
| `type` | server | server, client, email, code_signing |
| `dns_names` | [FQDN, hostname] | DNS SAN entries |
| `ip_addresses` | [default_ipv4] | IP SAN entries |
| `validity` | 365 | Days |
| `format` | pem | pem, p12, pfx |
| `password` | - | Required for p12/pfx |
| `notify` | [] | Handlers to trigger |

### Installed Files (PEM format)

| File | Location | Permissions |
|------|----------|-------------|
| Certificate | `/etc/ssl/certs/<name>.crt` | 0644 root:root |
| Private Key | `/etc/ssl/private/<name>.key` | 0640 root:ssl-cert |
| CA Chain | `/etc/ssl/certs/<name>-chain.crt` | 0644 root:root |
| Full Chain | `/etc/ssl/certs/<name>-fullchain.crt` | 0644 root:root |

See [roles/pki_host_setup/README.md](roles/pki_host_setup/README.md) for complete documentation.

## Available Actions

| Action | Description | Required Parameters |
|--------|-------------|---------------------|
| `auth_test` | Test authentication | - |
| `stats` | Get PKI statistics | - |
| `expiring` | List expiring certificates | - |
| `search` | Search CAs and certificates | `search_query` |
| `ca_create` | Create a CA | `ca_cn`, `ca_org`, `ca_country` |
| `ca_list` | List CAs | - |
| `ca_get` | Get CA details | `ca_id` |
| `ca_revoke` | Revoke a CA | `ca_id` |
| `ca_delete` | Delete a CA | `ca_id` |
| `cert_issue` | Issue a certificate | `ca_id`, `cert_cn` |
| `cert_list` | List certificates | - |
| `cert_get` | Get certificate details | `cert_id` |
| `cert_renew` | Renew a certificate | `cert_id` |
| `cert_revoke` | Revoke a certificate | `cert_id` |
| `cert_delete` | Delete a certificate | `cert_id` |
| `cert_download` | Download certificate | `cert_id` |

## Module Parameters

### Connection Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `action` | Yes | - | Action to perform (see table above) |
| `api_url` | Yes | - | PKI Manager API URL |
| `oidc_url` | Yes | - | OIDC token endpoint |
| `client_id` | Yes | - | OIDC client ID |
| `client_secret` | Yes | - | OIDC client secret |
| `validate_certs` | No | `true` | Validate SSL certificates |
| `timeout` | No | `30` | Request timeout (seconds) |
| `token_cache_path` | No | `/tmp/.pki_token_cache` | Token cache file path |

### CA Parameters

| Parameter | Description |
|-----------|-------------|
| `ca_id` | CA ID (for operations on existing CA) |
| `ca_cn` | Common Name |
| `ca_org` | Organization |
| `ca_country` | Country (2-letter code) |
| `ca_ou` | Organizational Unit |
| `ca_state` | State/Province |
| `ca_locality` | Locality/City |
| `ca_algorithm` | Key algorithm: `RSA-2048`, `RSA-4096`, `ECDSA-P256`, `ECDSA-P384` |
| `ca_validity` | Validity in days (default: 3650) |

### Certificate Parameters

| Parameter | Description |
|-----------|-------------|
| `cert_id` | Certificate ID |
| `cert_cn` | Common Name |
| `cert_org` | Organization |
| `cert_country` | Country (2-letter code) |
| `cert_type` | Type: `server`, `client`, `email`, `code_signing` |
| `cert_algorithm` | Key algorithm (default: `RSA-2048`) |
| `cert_validity` | Validity in days (default: 365) |
| `cert_dns_names` | List of DNS SANs |
| `cert_ip_addresses` | List of IP SANs |
| `cert_emails` | List of email SANs |

### Download Parameters

| Parameter | Description |
|-----------|-------------|
| `download_format` | Format: `pem`, `der`, `p12`, `pfx`, `jks-keystore`, `jks-truststore`, `full-pem`, `chain-pem`, `key-pem` |
| `download_password` | Password for encrypted formats (required for p12, pfx, jks-*) |
| `download_dest` | Destination file path |

### Other Parameters

| Parameter | Description |
|-----------|-------------|
| `revocation_reason` | Revocation reason: `unspecified`, `keyCompromise`, `superseded`, etc. |
| `search_query` | Search query string |
| `search_limit` | Max search results (default: 10) |
| `expiring_limit` | Max expiring certs (default: 5, max: 20) |

## Return Values

| Key | Actions | Description |
|-----|---------|-------------|
| `ca` | ca_create, ca_get | CA details |
| `ca_id` | ca_create | Created CA ID |
| `cas` | ca_list | List of CAs |
| `ca_count` | ca_list | Total CA count |
| `certificate` | cert_issue, cert_get, cert_renew | Certificate details |
| `cert_id` | cert_issue | Issued certificate ID |
| `new_cert_id` | cert_renew | Renewed certificate ID |
| `certificates` | cert_list | List of certificates |
| `cert_count` | cert_list | Total certificate count |
| `stats` | stats | PKI statistics |
| `search_results` | search | Search results (cas, certificates, domains) |
| `total_count` | search | Total search results |
| `expiring` | expiring | List of expiring certificates |
| `downloaded_file` | cert_download | Downloaded file path |
| `msg` | all | Status message |
| `changed` | all | Whether changes were made |

## Examples

### Create CA and Issue Certificate

```yaml
- name: Create Root CA
  oriolrius.pki_manager.pki_manager:
    action: ca_create
    api_url: "{{ api_url }}"
    oidc_url: "{{ oidc_url }}"
    client_id: "{{ client_id }}"
    client_secret: "{{ client_secret }}"
    ca_cn: "My Root CA"
    ca_org: "My Organization"
    ca_country: "US"
    ca_validity: 3650
  register: ca

- name: Issue Server Certificate
  oriolrius.pki_manager.pki_manager:
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
    cert_dns_names:
      - "webserver.example.com"
      - "www.example.com"
    cert_ip_addresses:
      - "192.168.1.100"
  register: cert
```

### Download in Multiple Formats

```yaml
- name: Download as PEM (certificate + chain)
  oriolrius.pki_manager.pki_manager:
    action: cert_download
    api_url: "{{ api_url }}"
    oidc_url: "{{ oidc_url }}"
    client_id: "{{ client_id }}"
    client_secret: "{{ client_secret }}"
    cert_id: "{{ cert.cert_id }}"
    download_format: "full-pem"
    download_dest: "/etc/ssl/certs/server.pem"

- name: Download as PKCS12
  oriolrius.pki_manager.pki_manager:
    action: cert_download
    api_url: "{{ api_url }}"
    oidc_url: "{{ oidc_url }}"
    client_id: "{{ client_id }}"
    client_secret: "{{ client_secret }}"
    cert_id: "{{ cert.cert_id }}"
    download_format: "p12"
    download_password: "{{ vault_p12_password }}"
    download_dest: "/etc/ssl/private/server.p12"
```

### Monitor Expiring Certificates

```yaml
- name: Get expiring certificates
  oriolrius.pki_manager.pki_manager:
    action: expiring
    api_url: "{{ api_url }}"
    oidc_url: "{{ oidc_url }}"
    client_id: "{{ client_id }}"
    client_secret: "{{ client_secret }}"
    expiring_limit: 20
  register: expiring

- name: Alert on certificates expiring soon
  ansible.builtin.debug:
    msg: "WARNING: {{ item.cn }} expires in {{ item.daysRemaining }} days!"
  loop: "{{ expiring.expiring }}"
  when: item.daysRemaining | int < 30
```

### Renew and Revoke

```yaml
- name: Renew certificate
  oriolrius.pki_manager.pki_manager:
    action: cert_renew
    api_url: "{{ api_url }}"
    oidc_url: "{{ oidc_url }}"
    client_id: "{{ client_id }}"
    client_secret: "{{ client_secret }}"
    cert_id: "{{ old_cert_id }}"
    cert_validity: 365
  register: renewed

- name: Revoke old certificate
  oriolrius.pki_manager.pki_manager:
    action: cert_revoke
    api_url: "{{ api_url }}"
    oidc_url: "{{ oidc_url }}"
    client_id: "{{ client_id }}"
    client_secret: "{{ client_secret }}"
    cert_id: "{{ old_cert_id }}"
    revocation_reason: "superseded"
```

## Testing

```bash
# Set credentials
export PKI_API_URL="https://pki.example.com/api/v1"
export PKI_OIDC_URL="https://iam.example.com/realms/pki/protocol/openid-connect/token"
export PKI_CLIENT_ID="your-client-id"
export PKI_CLIENT_SECRET="your-client-secret"

# Build and install collection locally
ansible-galaxy collection build
ansible-galaxy collection install oriolrius-pki_manager-*.tar.gz --force

# Run tests
ansible-playbook tests/test_module.yml
```

## License

MIT

## Author

Oriol Rius - [joor.net](https://joor.net)

## Related Projects

| Project | Description |
|---------|-------------|
| [PKI Manager](https://github.com/oriolrius/pki-manager-web) | Main PKI Manager web application |
| [PKI Manager CLI](https://github.com/oriolrius/pki-manager-cli) | Python CLI tool for PKI Manager |
| [PKI Manager Skill](https://github.com/oriolrius/pki-manager-skill) | Claude Code skill for AI-assisted certificate management |
