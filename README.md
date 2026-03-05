# PKI Manager Ansible Role

Ansible role and module for managing X.509 certificates via the PKI Manager API.

## Features

- 🔐 OIDC authentication with token caching
- 🏛️ CA management (create, list, get, revoke, delete)
- 📜 Certificate management (issue, list, get, renew, revoke, delete)
- 📥 Certificate download in multiple formats (PEM, DER, P12, JKS, etc.)
- 🔍 Search across CAs and certificates
- 📊 Statistics and expiring certificates dashboard
- ✅ Python module for better maintainability

## Installation

### Using requirements.yml

```yaml
# requirements.yml
- src: https://github.com/oriolrius/pki-manager-role.git
  scm: git
  version: v1.0.0
  name: pki_manager
```

```bash
ansible-galaxy install -r requirements.yml
```

### Manual Installation

```bash
git clone https://github.com/oriolrius/pki-manager-role.git
# Add to ansible.cfg
echo "roles_path = /path/to/pki-manager-role/roles" >> ansible.cfg
echo "library = /path/to/pki-manager-role/roles/pki_manager/library" >> ansible.cfg
```

## Quick Start

### Configure Credentials

```yaml
# group_vars/all.yml
pki_api_url: "https://pki.example.com/api/v1"
pki_oidc_url: "https://iam.example.com/realms/pki/protocol/openid-connect/token"
pki_client_id: "ansible-pki"
pki_client_secret: "{{ vault_pki_client_secret }}"  # Use Ansible Vault!
```

Or use environment variables:

```bash
export PKI_API_URL="https://pki.example.com/api/v1"
export PKI_OIDC_URL="https://iam.example.com/realms/pki/protocol/openid-connect/token"
export PKI_CLIENT_ID="your-client-id"
export PKI_CLIENT_SECRET="your-client-secret"
```

## Usage

### Option 1: Use the Module Directly (Recommended)

The `pki_manager` module provides a cleaner, more maintainable approach:

```yaml
- name: Issue a certificate
  pki_manager:
    action: cert_issue
    api_url: "{{ pki_api_url }}"
    oidc_url: "{{ pki_oidc_url }}"
    client_id: "{{ pki_client_id }}"
    client_secret: "{{ pki_client_secret }}"
    ca_id: "your-ca-id"
    cert_cn: "server.example.com"
    cert_org: "My Organization"
    cert_country: "US"
    cert_type: "server"
    cert_dns_names:
      - "server.example.com"
      - "www.example.com"
    cert_validity: 365
  register: cert_result

- name: Download certificate as P12
  pki_manager:
    action: cert_download
    api_url: "{{ pki_api_url }}"
    oidc_url: "{{ pki_oidc_url }}"
    client_id: "{{ pki_client_id }}"
    client_secret: "{{ pki_client_secret }}"
    cert_id: "{{ cert_result.cert_id }}"
    download_format: "p12"
    download_password: "{{ vault_cert_password }}"
    download_dest: "/etc/ssl/certs/server.p12"
```

### Option 2: Use the Role (Legacy)

```yaml
- name: Issue a certificate
  ansible.builtin.include_role:
    name: pki_manager
  vars:
    pki_action: cert_issue
    pki_ca_id: "your-ca-id"
    pki_cert_cn: "server.example.com"
    pki_cert_type: server
    pki_cert_dns_names:
      - "server.example.com"
```

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
| `api_url` | Yes | - | PKI Manager API URL |
| `oidc_url` | Yes | - | OIDC token endpoint |
| `client_id` | Yes | - | OIDC client ID |
| `client_secret` | Yes | - | OIDC client secret |
| `validate_certs` | No | `true` | Validate SSL certificates |
| `timeout` | No | `30` | Request timeout (seconds) |

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
| `cert_id` | Certificate ID (for operations on existing cert) |
| `cert_cn` | Common Name |
| `cert_org` | Organization |
| `cert_country` | Country (2-letter code) |
| `cert_type` | Type: `server`, `client`, `email`, `code_signing` |
| `cert_algorithm` | Key algorithm |
| `cert_validity` | Validity in days (default: 365) |
| `cert_dns_names` | List of DNS SANs |
| `cert_ip_addresses` | List of IP SANs |
| `cert_emails` | List of email SANs |

### Download Parameters

| Parameter | Description |
|-----------|-------------|
| `download_format` | Format: `pem`, `der`, `p12`, `pfx`, `jks-keystore`, etc. |
| `download_password` | Password for encrypted formats |
| `download_dest` | Destination file path |

### Other Parameters

| Parameter | Description |
|-----------|-------------|
| `revocation_reason` | Revocation reason (default: `unspecified`) |
| `search_query` | Search query string |
| `search_limit` | Max search results (default: 10) |
| `expiring_limit` | Max expiring certs (default: 5, max: 20) |

## Return Values

| Key | Description |
|-----|-------------|
| `ca` | CA details (ca_create, ca_get) |
| `ca_id` | Created/retrieved CA ID |
| `cas` | List of CAs (ca_list) |
| `certificate` | Certificate details (cert_issue, cert_get, cert_renew) |
| `cert_id` | Created/retrieved certificate ID |
| `new_cert_id` | New certificate ID (cert_renew) |
| `certificates` | List of certificates (cert_list) |
| `stats` | PKI statistics (stats) |
| `search_results` | Search results (search) |
| `expiring` | Expiring certificates (expiring) |
| `downloaded_file` | Downloaded file path (cert_download) |

## Examples

### Create a CA and Issue Certificates

```yaml
- name: Setup PKI
  hosts: localhost
  vars:
    pki_api_url: "https://pki.example.com/api/v1"
    pki_oidc_url: "https://iam.example.com/realms/pki/protocol/openid-connect/token"
    pki_client_id: "{{ lookup('env', 'PKI_CLIENT_ID') }}"
    pki_client_secret: "{{ lookup('env', 'PKI_CLIENT_SECRET') }}"

  tasks:
    - name: Create Root CA
      pki_manager:
        action: ca_create
        api_url: "{{ pki_api_url }}"
        oidc_url: "{{ pki_oidc_url }}"
        client_id: "{{ pki_client_id }}"
        client_secret: "{{ pki_client_secret }}"
        ca_cn: "My Root CA"
        ca_org: "My Organization"
        ca_country: "US"
        ca_validity: 3650
      register: ca_result

    - name: Issue Server Certificate
      pki_manager:
        action: cert_issue
        api_url: "{{ pki_api_url }}"
        oidc_url: "{{ pki_oidc_url }}"
        client_id: "{{ pki_client_id }}"
        client_secret: "{{ pki_client_secret }}"
        ca_id: "{{ ca_result.ca_id }}"
        cert_cn: "webserver.example.com"
        cert_org: "My Organization"
        cert_country: "US"
        cert_type: "server"
        cert_dns_names:
          - "webserver.example.com"
          - "www.example.com"
      register: cert_result

    - name: Download as PEM
      pki_manager:
        action: cert_download
        api_url: "{{ pki_api_url }}"
        oidc_url: "{{ pki_oidc_url }}"
        client_id: "{{ pki_client_id }}"
        client_secret: "{{ pki_client_secret }}"
        cert_id: "{{ cert_result.cert_id }}"
        download_format: "full-pem"
        download_dest: "/etc/ssl/certs/webserver.pem"
```

### Monitor Expiring Certificates

```yaml
- name: Check expiring certificates
  pki_manager:
    action: expiring
    api_url: "{{ pki_api_url }}"
    oidc_url: "{{ pki_oidc_url }}"
    client_id: "{{ pki_client_id }}"
    client_secret: "{{ pki_client_secret }}"
    expiring_limit: 20
  register: expiring

- name: Alert on expiring certificates
  ansible.builtin.debug:
    msg: "Certificate {{ item.cn }} expires in {{ item.daysRemaining }} days!"
  loop: "{{ expiring.expiring }}"
  when: item.daysRemaining | int < 30
```

## Testing

```bash
# Set environment variables
export PKI_API_URL="https://pki.example.com/api/v1"
export PKI_OIDC_URL="https://iam.example.com/realms/pki/protocol/openid-connect/token"
export PKI_CLIENT_ID="your-client-id"
export PKI_CLIENT_SECRET="your-client-secret"

# Run module tests
cd pki-manager-role
ANSIBLE_LIBRARY=./roles/pki_manager/library \
  ansible-playbook roles/pki_manager/tests/test_module.yml

# Run legacy role tests
ANSIBLE_ROLES_PATH=./roles \
  ansible-playbook -i roles/pki_manager/tests/inventory \
  roles/pki_manager/tests/test.yml
```

## License

MIT

## Author

Oriol Rius - [joor.net](https://joor.net)

## Related Projects

- [PKI Manager](https://github.com/oriolrius/pki-manager) - Main PKI Manager application
- [PKI Manager CLI](https://github.com/oriolrius/pki-manager-cli) - Python CLI tool
- [PKI Manager Skill](https://github.com/oriolrius/pki-manager-skill) - Claude Code skill
