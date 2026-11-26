#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Oriol Rius
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: pki_manager
short_description: Manage PKI Manager certificates and CAs
version_added: "1.0.0"
description:
    - Manage Certificate Authorities (CAs) and certificates using PKI Manager API.
    - Supports OIDC authentication with token caching.
    - All operations are idempotent where applicable.
options:
    action:
        description:
            - The action to perform.
        required: true
        type: str
        choices:
            - auth_test
            - stats
            - expiring
            - search
            - ca_create
            - ca_list
            - ca_get
            - ca_revoke
            - ca_delete
            - cert_issue
            - cert_list
            - cert_get
            - cert_renew
            - cert_revoke
            - cert_delete
            - cert_download
            - cert_find
            - ssh_ca_create
            - ssh_ca_list
            - ssh_token_mint
            - ssh_identity_create
            - ssh_principal_create
            - ssh_principal_grant
            - ssh_principal_map
            - ssh_user_issue
            - ssh_host_register
            - ssh_host_list
            - ssh_block
            - ssh_unblock
            - ssh_auth_principals
            - ssh_sshd_config
            - ssh_cert_authority
            - ssh_trusted_user_ca
            - ssh_host_ca
            - ssh_sign_host
            - ssh_register_host_pubkey
            - ssh_get_principals
            - ssh_principals_pushed
            - ssh_zone_list
            - ssh_zone_create
    api_url:
        description:
            - PKI Manager API URL.
        required: true
        type: str
    oidc_url:
        description:
            - OIDC token endpoint URL.
            - Set it with O(client_id) and O(client_secret) for the OIDC client-credentials login.
            - Omit all three for a server with OIDC disabled, for O(api_token), or for the fleet-token actions.
        type: str
    client_id:
        description:
            - OIDC client ID.
        type: str
    client_secret:
        description:
            - OIDC client secret.
        type: str
    api_token:
        description:
            - A bearer token that you got before (for example from a CI step). The module then does not call O(oidc_url).
            - It has priority over the OIDC credentials.
        type: str
    ca_path:
        description:
            - PEM file with the CA certificates to trust for HTTPS to the PKI Manager server and the OIDC server.
            - Use it for a server with a private CA, instead of O(validate_certs=false).
        type: path
    ca_id:
        description:
            - Certificate Authority ID (required for CA operations and cert_issue).
        type: str
    ca_cn:
        description:
            - CA Common Name (required for ca_create).
        type: str
    ca_org:
        description:
            - CA Organization (required for ca_create).
        type: str
    ca_country:
        description:
            - CA Country code (2 letters, required for ca_create).
        type: str
    ca_ou:
        description:
            - CA Organizational Unit.
        type: str
    ca_state:
        description:
            - CA State/Province.
        type: str
    ca_locality:
        description:
            - CA Locality/City.
        type: str
    ca_algorithm:
        description:
            - Key algorithm for CA. The API accepts only RSA keys for a CA.
        type: str
        choices: ['RSA-2048', 'RSA-4096']
        default: 'RSA-4096'
    ca_validity_years:
        description:
            - CA validity in years (1-30). The server default is 20.
        type: int
    ca_validity:
        description:
            - Deprecated. CA validity in days; the module rounds it to years (the API takes years only).
            - Use O(ca_validity_years). Before 3.0.0 the server ignored this value and used 20 years.
        type: int
    cert_id:
        description:
            - Certificate ID (required for cert operations except cert_issue).
        type: str
    cert_cn:
        description:
            - Certificate Common Name (required for cert_issue).
        type: str
    cert_org:
        description:
            - Certificate Organization (required for cert_issue; the API requires it).
        type: str
    cert_country:
        description:
            - Certificate Country code, 2 letters (required for cert_issue; the API requires it).
        type: str
    cert_ou:
        description:
            - Certificate Organizational Unit.
        type: str
    cert_state:
        description:
            - Certificate State/Province.
        type: str
    cert_locality:
        description:
            - Certificate Locality/City.
        type: str
    cert_type:
        description:
            - Certificate type. For cert_issue the default is V(server).
            - For cert_list it is a filter; omit it to list every type.
        type: str
        choices: ['server', 'client', 'dual', 'email', 'code_signing']
    cert_status:
        description:
            - Filter for cert_list.
        type: str
        choices: ['active', 'revoked', 'expired']
    cert_algorithm:
        description:
            - Key algorithm for certificate.
        type: str
        choices: ['RSA-2048', 'RSA-4096', 'ECDSA-P256', 'ECDSA-P384']
        default: 'RSA-2048'
    cert_validity:
        description:
            - Certificate validity in days.
        type: int
        default: 365
    cert_dns_names:
        description:
            - List of DNS names for SAN.
        type: list
        elements: str
    cert_ip_addresses:
        description:
            - List of IP addresses for SAN.
        type: list
        elements: str
    cert_emails:
        description:
            - List of email addresses for SAN.
        type: list
        elements: str
    revocation_reason:
        description:
            - Reason for revocation.
        type: str
        choices:
            - unspecified
            - keyCompromise
            - caCompromise
            - affiliationChanged
            - superseded
            - cessationOfOperation
            - certificateHold
            - removeFromCRL
        default: 'unspecified'
    revocation_details:
        description: Free-text detail recorded with the revocation (cert_revoke, ca_revoke).
        type: str
    cert_pem:
        description:
            - PEM of a certificate for cert_find. The module reads its serial number (Python C(cryptography))
              and returns the certificate with that serial.
        type: str
    download_format:
        description:
            - Certificate download format.
            - V(chain-pem) is certificate + issuing CA, V(full-pem) is certificate + private key + issuing CA
              (PKI Manager 3.19.1 and later; before, chain-pem had no CA and full-pem had no chain).
        type: str
        choices:
            - pem
            - der
            - chain-pem
            - full-pem
            - full-der
            - key-pem
            - key-der
            - csr-pem
            - p12
            - pfx
            - pkcs8-pem
            - pkcs8-der
            - pkcs8-encrypted
            - jks-keystore
            - jks-truststore
        default: 'pem'
    download_password:
        description:
            - Password for encrypted formats (p12, pfx, jks-*, pkcs8-encrypted).
            - The module sends it in the C(X-Export-Password) header, never in the URL.
        type: str
    download_dest:
        description:
            - Destination path for downloaded certificate (written with mode 0600).
            - When the file already has the same content and mode, nothing changes (C(changed=false)).
        type: path
    search_query:
        description:
            - Search query string.
        type: str
    search_limit:
        description:
            - Maximum search results.
        type: int
        default: 10
    expiring_limit:
        description:
            - Maximum expiring certificates to return.
        type: int
        default: 5
    validate_certs:
        description:
            - Whether to validate SSL certificates.
        type: bool
        default: true
    timeout:
        description:
            - API request timeout in seconds.
        type: int
        default: 30
    token_cache_path:
        description:
            - File for the OIDC token cache.
            - The default is a file in C(~/.cache/pki-manager-ansible/) (mode 0700) with a name made from
              O(api_url), O(oidc_url) and O(client_id), so two servers or two clients never share a token.
            - The module uses a cache file only when the current user owns it, nobody else can read it,
              and it was written for the same server and client.
        type: path
    fleet_token:
        description:
            - Fleet bearer token (pkimg_...) for the host-facing external SSH API
              (ssh_sign_host, ssh_register_host_pubkey, ssh_get_principals, ssh_principals_pushed).
        type: str
    principals_sha256:
        description:
            - Canonical sha256 (64 hex, a C(sha256:) prefix is accepted) of the principal files the host installed,
              as returned in C(auth_principals.sha256) by C(ssh_get_principals). Required for C(ssh_principals_pushed).
            - The backend answers 409 SHA256_MISMATCH when it is not the hash of the current render; the action then fails
              with C(sha256_mismatch=true) and C(current_sha256) so the caller can fetch and install again.
        type: str
    ssh_ca_type:
        description: SSH CA type for ssh_ca_create.
        type: str
        choices: ['user', 'host']
    ssh_ca_label:
        description: Optional label for ssh_ca_create.
        type: str
    token_name:
        description: Name of the fleet token (ssh_token_mint).
        type: str
    token_ops:
        description: Op-set for the fleet token (ssh_token_mint), e.g. sign-host, get-principals, register-host-pubkey.
        type: list
        elements: str
    host_ca_id:
        description: Host CA id (ssh_token_mint).
        type: str
    user_ca_id:
        description: User CA id (ssh_token_mint, ssh_user_issue).
        type: str
    identity_id:
        description: SSH identity id.
        type: str
    identity_subject:
        description: Subject for ssh_identity_create.
        type: str
    identity_email:
        description: Optional email for ssh_identity_create.
        type: str
    principal_id:
        description: Principal id (ssh_principal_grant, ssh_principal_map).
        type: str
    principal_name:
        description: Principal name for ssh_principal_create.
        type: str
    principal_description:
        description: Optional description for ssh_principal_create.
        type: str
    host_id:
        description: Server-side host id (ssh_principal_map, ssh_block, ssh_auth_principals, ssh_sshd_config).
        type: str
    host_fqdn:
        description: Host FQDN (ssh_host_register/list, ssh_sign_host, ssh_register_host_pubkey, ssh_get_principals).
        type: str
    host_pubkey:
        description: Host OpenSSH public key (ssh_host_register, ssh_sign_host).
        type: str
    host_addresses:
        description: Host IP addresses (ssh_host_register, ssh_sign_host).
        type: list
        elements: str
    local_account:
        description: Local UNIX account for ssh_principal_map.
        type: str
    ssh_public_key:
        description: User OpenSSH public key for ssh_user_issue.
        type: str
    principals:
        description: Principals to encode in the user certificate (ssh_user_issue).
        type: list
        elements: str
    user_valid_seconds:
        description:
            - Validity in seconds for the user cert (ssh_user_issue).
            - For ssh_sign_host it is used only when O(host_valid_seconds) is not set (old behaviour).
        type: int
    host_valid_seconds:
        description: Validity in seconds for the signed host cert (ssh_sign_host).
        type: int
    host_key_id:
        description: Optional certificate key id for ssh_sign_host.
        type: str
    identity_external_subject:
        description: Optional external (IdP) subject for ssh_identity_create.
        type: str
    enforce_entitlement:
        description: Constrain issued principals to the identity's catalog entitlements (ssh_user_issue).
        type: bool
    cert_authority_pattern:
        description: known_hosts pattern for ssh_cert_authority.
        type: str
        default: '*'
    block_reason:
        description: Optional reason for ssh_block.
        type: str
    idempotency_key:
        description: Idempotency-Key header for ssh_sign_host.
        type: str
    zone:
        description:
            - SSH zone, by id or name (decision-017 multi-tenant SSH).
            - Sent with ssh_ca_create, ssh_token_mint, ssh_identity_create, ssh_principal_create and ssh_host_register.
              With two or more zones the server refuses these without a zone (fail-closed).
            - Filters ssh_ca_list and ssh_host_list.
            - Selects the zone of ssh_trusted_user_ca, ssh_host_ca and ssh_cert_authority
              (C(/ssh/zones/<zone>/...)). Without it they return the DEFAULT zone only (old, deprecated URLs).
            - Name of the new zone for ssh_zone_create.
            - Not used by the fleet-token actions; the fleet token sets the zone there.
        type: str
    zone_display_name:
        description: Display name for ssh_zone_create.
        type: str
    zone_description:
        description: Description for ssh_zone_create.
        type: str
author:
    - Oriol Rius (@oriolrius)
'''

EXAMPLES = r'''
- name: Test authentication
  pki_manager:
    action: auth_test
    api_url: "https://pki.example.com/api/v1"
    oidc_url: "https://iam.example.com/realms/pki/protocol/openid-connect/token"
    client_id: "pki-service"
    client_secret: "{{ pki_secret }}"

- name: Get PKI statistics
  pki_manager:
    action: stats
    api_url: "{{ pki_api_url }}"
    oidc_url: "{{ pki_oidc_url }}"
    client_id: "{{ pki_client_id }}"
    client_secret: "{{ pki_client_secret }}"
  register: stats

- name: Create a CA
  pki_manager:
    action: ca_create
    api_url: "{{ pki_api_url }}"
    oidc_url: "{{ pki_oidc_url }}"
    client_id: "{{ pki_client_id }}"
    client_secret: "{{ pki_client_secret }}"
    ca_cn: "My Root CA"
    ca_org: "My Organization"
    ca_country: "US"
    ca_validity_years: 10
  register: ca_result

- name: Issue a certificate
  pki_manager:
    action: cert_issue
    api_url: "{{ pki_api_url }}"
    oidc_url: "{{ pki_oidc_url }}"
    client_id: "{{ pki_client_id }}"
    client_secret: "{{ pki_client_secret }}"
    ca_id: "{{ ca_result.ca.id }}"
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
    cert_id: "{{ cert_result.certificate.id }}"
    download_format: "p12"
    download_password: "mypassword"
    download_dest: "/tmp/cert.p12"

- name: Search for certificates
  pki_manager:
    action: search
    api_url: "{{ pki_api_url }}"
    oidc_url: "{{ pki_oidc_url }}"
    client_id: "{{ pki_client_id }}"
    client_secret: "{{ pki_client_secret }}"
    search_query: "example.com"
  register: search_result
'''

RETURN = r'''
changed:
    description: Whether any changes were made.
    type: bool
    returned: always
ca:
    description: CA details (for ca_create, ca_get).
    type: dict
    returned: when action is ca_create or ca_get
    sample:
        id: "abc123"
        subjectDn: "CN=My CA,O=My Org,C=US"
        status: "active"
cas:
    description: List of CAs (for ca_list).
    type: list
    returned: when action is ca_list
certificate:
    description: Certificate details (for cert_issue, cert_get, cert_renew).
    type: dict
    returned: when action is cert_issue, cert_get, or cert_renew
certificates:
    description: List of certificates (for cert_list).
    type: list
    returned: when action is cert_list
stats:
    description: PKI statistics (for stats action).
    type: dict
    returned: when action is stats
search_results:
    description: Search results (for search action).
    type: dict
    returned: when action is search
expiring:
    description: List of expiring certificates (for expiring action).
    type: list
    returned: when action is expiring
downloaded_file:
    description: Path to downloaded file (for cert_download).
    type: str
    returned: when action is cert_download
sha256_mismatch:
    description: True when the backend refused the acknowledgement with 409 SHA256_MISMATCH (ssh_principals_pushed; the action fails).
    type: bool
    returned: when action is ssh_principals_pushed and the hash is not the current render
current_sha256:
    description: Hash of the current principal render, sent by the backend with the 409 (ssh_principals_pushed).
    type: str
    returned: when sha256_mismatch is true
principals_pushed:
    description: Backend acknowledgement (hostId, fqdn, lastPrincipalPushAt, sha256) for ssh_principals_pushed.
    type: dict
    returned: when action is ssh_principals_pushed and it succeeded
msg:
    description: Status message.
    type: str
    returned: always
'''

import json
import os
import time
import base64
import hashlib
import tempfile
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url

try:
    from urllib.parse import urlencode, quote
except ImportError:
    from urllib import urlencode, quote


def default_token_cache_path(api_url, oidc_url, client_id):
    """Per-user cache file whose name is bound to the server and the client."""
    key = '|'.join([api_url or '', oidc_url or '', client_id or ''])
    digest = hashlib.sha256(key.encode('utf-8')).hexdigest()[:24]
    base = os.path.join(os.path.expanduser('~'), '.cache', 'pki-manager-ansible')
    return os.path.join(base, 'token-%s.json' % digest)


class PKIManagerClient:
    """Client for PKI Manager API operations."""

    def __init__(self, module, api_url, oidc_url, client_id, client_secret,
                 validate_certs=True, timeout=30, token_cache_path=None,
                 fleet_token=None, api_token=None, ca_path=None):
        self.module = module
        self.api_url = api_url.rstrip('/')
        self.oidc_url = oidc_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.validate_certs = validate_certs
        self.timeout = timeout
        self.ca_path = ca_path
        self.token_cache_path = token_cache_path or default_token_cache_path(
            self.api_url, oidc_url, client_id)
        # Fleet bearer token (pkimg_…) for the host-facing external SSH API.
        self.fleet_token = fleet_token
        self.api_token = api_token
        self.access_token = None
        self.token_from_cache = False

    def _open(self, url, **kwargs):
        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('validate_certs', self.validate_certs)
        if self.ca_path:
            kwargs.setdefault('ca_path', self.ca_path)
        return open_url(url, **kwargs)

    def has_credentials(self):
        return bool(self.api_token or (self.oidc_url and self.client_id and self.client_secret))

    def authenticate(self, use_cache=True):
        """Get the bearer token for the management API.

        Authentication is OPTIONAL: with no api_token and no client credentials
        the client makes unauthenticated requests. That covers a backend running
        with OIDC disabled, and the SSH host-facing actions which authenticate
        with a fleet_token instead.
        """
        if self.api_token:
            self.access_token = self.api_token
            return True
        if not (self.oidc_url and self.client_id and self.client_secret):
            return False
        if use_cache and self._load_cached_token():
            self.token_from_cache = True
            return True
        self.token_from_cache = False

        data = urlencode({
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        })
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        try:
            response = self._open(self.oidc_url, data=data, headers=headers, method='POST')
            token_data = json.loads(response.read())
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 300)
            self._cache_token(expires_in)
            return True
        except Exception as e:
            self.module.fail_json(msg=f"OIDC authentication failed: {e}")

    def _cache_identity(self):
        return {'api_url': self.api_url, 'oidc_url': self.oidc_url, 'client_id': self.client_id}

    def _load_cached_token(self):
        """Load the token from the cache when the file is safe and for this server/client."""
        path = self.token_cache_path
        try:
            st = os.lstat(path)
        except OSError:
            return False
        # Never use a file another user could have written or can read.
        if (not os.path.isfile(path) or os.path.islink(path)
                or st.st_uid != os.geteuid() or st.st_mode & 0o077):
            return False
        try:
            with open(path, 'r') as f:
                cache = json.load(f)
        except (IOError, OSError, ValueError):
            return False
        if cache.get('identity') != self._cache_identity():
            return False
        if cache.get('expires_at', 0) > time.time() + 60:  # 60s buffer
            self.access_token = cache['access_token']
            return True
        return False

    def _cache_token(self, expires_in):
        """Write the cache atomically, mode 0600, in a 0700 directory."""
        path = self.token_cache_path
        try:
            directory = os.path.dirname(path) or '.'
            if not os.path.isdir(directory):
                os.makedirs(directory, 0o700)
            fd, tmp = tempfile.mkstemp(dir=directory, prefix='.token-')  # mode 0600
            try:
                with os.fdopen(fd, 'w') as f:
                    json.dump({
                        'identity': self._cache_identity(),
                        'access_token': self.access_token,
                        'expires_at': time.time() + expires_in,
                    }, f)
                os.replace(tmp, path)
            except BaseException:
                if os.path.exists(tmp):
                    os.unlink(tmp)
                raise
        except (IOError, OSError):
            pass  # Caching is optional

    def _clear_cached_token(self):
        try:
            os.unlink(self.token_cache_path)
        except OSError:
            pass

    def _request(self, method, endpoint, data=None, params=None, extra_headers=None, _retried=False):
        """Make an authenticated API request."""
        url = f"{self.api_url}{endpoint}"
        if params:
            url = f"{url}?{urlencode(params)}"

        headers = {}
        if self.access_token:
            headers['Authorization'] = f"Bearer {self.access_token}"
        if extra_headers:
            headers.update(extra_headers)

        body = None
        if data is not None:
            headers['Content-Type'] = 'application/json'
            body = json.dumps(data)

        try:
            response = self._open(url, data=body, headers=headers, method=method)
            status = response.getcode()
            try:
                response_data = json.loads(response.read())
                return {'status': status, 'data': response_data, 'error': None}
            except (json.JSONDecodeError, ValueError):
                return {'status': status, 'data': None, 'error': None}
        except Exception as e:
            err = self._err(e)
            # A cached token the server refuses (revoked, server key rotated):
            # drop the cache, log in again and retry once.
            if err['status'] == 401 and self.token_from_cache and not _retried:
                self._clear_cached_token()
                self.authenticate(use_cache=False)
                return self._request(method, endpoint, data, params, extra_headers, _retried=True)
            return err

    @staticmethod
    def _error_message(error_data, default):
        """Read the message from both error shapes of the API.

        Application errors: {"error": {"code": ..., "message": ...}}.
        Fastify validation errors: {"error": "Bad Request", "message": ...}.
        """
        if not isinstance(error_data, dict):
            return default
        err = error_data.get('error')
        if isinstance(err, dict):
            msg = err.get('message') or default
            code = err.get('code')
            return f"{code}: {msg}" if code and code not in msg else msg
        if error_data.get('message'):
            return error_data['message']
        if isinstance(err, str) and err:
            return err
        return default

    def _err(self, e):
        """Normalize an open_url exception into {status, data, error}."""
        error_str = str(e)
        status = 500
        if hasattr(e, 'code'):
            status = e.code
        elif 'HTTP Error' in error_str:
            try:
                status = int(error_str.split('HTTP Error ')[1].split(':')[0])
            except (IndexError, ValueError):
                pass
        error_msg = error_str
        body = None
        if hasattr(e, 'read'):
            try:
                body = json.loads(e.read())
                error_msg = self._error_message(body, error_str)
            except Exception:
                pass
        if status == 404 and error_msg == error_str:
            error_msg = 'Not found'
        if status == 409 and error_msg == error_str:
            error_msg = 'Conflict - operation blocked'
        return {'status': status, 'data': None, 'error': error_msg, 'body': body}

    def get(self, endpoint, params=None, extra_headers=None):
        return self._request('GET', endpoint, params=params, extra_headers=extra_headers)

    def get_all(self, endpoint, params=None, page_size=100):
        """GET every page of a {items, pagination} list endpoint."""
        params = dict(params or {})
        items, offset = [], 0
        while True:
            params.update({'limit': page_size, 'offset': offset})
            r = self.get(endpoint, params=params)
            if r['error']:
                return r, items, 0
            data = r['data'] or {}
            page = data.get('items', [])
            items.extend(page)
            total = (data.get('pagination') or {}).get('total', len(items))
            offset += len(page)
            if not page or offset >= total:
                return r, items, total

    def post(self, endpoint, data=None):
        return self._request('POST', endpoint, data=data)

    def delete(self, endpoint):
        return self._request('DELETE', endpoint)

    # Action implementations
    def auth_test(self):
        """Test authentication against an endpoint that needs it (/health does not)."""
        health = self.get('/health')
        result = self.get('/dashboard/stats')
        if result['error']:
            return {'changed': False, 'failed': True,
                    'msg': f"Authentication failed: {result['error']}"}
        msg = 'Authentication successful'
        if not self.has_credentials():
            msg = 'No credentials configured; the server accepts anonymous requests (OIDC disabled)'
        return {'changed': False, 'msg': msg, 'authenticated': self.has_credentials(),
                'status': health['data']}

    def stats(self):
        """Get PKI statistics."""
        result = self.get('/dashboard/stats')
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        return {'changed': False, 'stats': result['data'], 'msg': 'Statistics retrieved'}

    def expiring(self, limit=5):
        """Get expiring certificates."""
        result = self.get('/dashboard/expiring', params={'limit': min(limit, 20)})
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        return {'changed': False, 'expiring': result['data'], 'msg': f"Found {len(result['data'])} expiring certificates"}

    def search(self, query, limit=10):
        """Search CAs and certificates."""
        result = self.get('/search', params={'query': query, 'limit': limit})
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        data = result['data']
        total = data.get('totalCount', 0)
        return {
            'changed': False,
            'search_results': data.get('results', {}),
            'total_count': total,
            'msg': f"Found {total} results for '{query}'",
        }

    def ca_create(self, cn, org, country, ou=None, state=None, locality=None,
                  algorithm='RSA-4096', validity_years=None):
        """Create a Certificate Authority."""
        payload = {
            'subject': {
                'commonName': cn,
                'organization': org,
                'country': country,
            },
            'keyAlgorithm': algorithm,
        }
        if validity_years:
            payload['validityYears'] = validity_years
        if ou:
            payload['subject']['organizationalUnit'] = ou
        if state:
            payload['subject']['state'] = state
        if locality:
            payload['subject']['locality'] = locality

        result = self.post('/cas/', payload)
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        return {
            'changed': True,
            'ca': result['data'],
            'ca_id': result['data']['id'],
            'msg': f"Created CA '{cn}' with ID: {result['data']['id']}",
        }

    def ca_list(self):
        """List Certificate Authorities."""
        result, items, total = self.get_all('/cas/')
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        return {
            'changed': False,
            'cas': items,
            'ca_count': total,
            'msg': f"Found {total} Certificate Authorities",
        }

    def ca_get(self, ca_id):
        """Get CA details."""
        result = self.get(f'/cas/{ca_id}')
        if result['status'] == 404:
            return {'changed': False, 'failed': True, 'msg': f"CA {ca_id} not found"}
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        return {'changed': False, 'ca': result['data'], 'msg': f"Retrieved CA {ca_id}"}

    def ca_revoke(self, ca_id, reason='unspecified', details=None):
        """Revoke a CA."""
        payload = {'reason': reason}
        if details:
            payload['details'] = details
        result = self.post(f'/cas/{ca_id}/revoke', payload)
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        return {'changed': True, 'msg': f"CA {ca_id} revoked with reason: {reason}"}

    def ca_delete(self, ca_id):
        """Delete a CA."""
        result = self.delete(f'/cas/{ca_id}')
        if result['status'] == 404:
            return {'changed': False, 'msg': f"CA {ca_id} not found (already deleted?)"}
        if result['status'] == 409:
            return {'changed': False, 'msg': f"CA {ca_id} cannot be deleted yet (must be revoked/expired for > 90 days)"}
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        return {'changed': True, 'msg': f"CA {ca_id} deleted"}

    def cert_issue(self, ca_id, cn, org=None, country=None, ou=None, state=None,
                   locality=None, cert_type=None, algorithm='RSA-2048',
                   validity=365, dns_names=None, ip_addresses=None, emails=None):
        """Issue a certificate."""
        payload = {
            'caId': ca_id,
            'subject': {'commonName': cn},
            'certificateType': cert_type or 'server',
            'keyAlgorithm': algorithm,
            'validityDays': validity,
        }
        if org:
            payload['subject']['organization'] = org
        if country:
            payload['subject']['country'] = country
        if ou:
            payload['subject']['organizationalUnit'] = ou
        if state:
            payload['subject']['state'] = state
        if locality:
            payload['subject']['locality'] = locality
        if dns_names:
            payload['sanDns'] = dns_names
        if ip_addresses:
            payload['sanIp'] = ip_addresses
        if emails:
            payload['sanEmail'] = emails

        result = self.post('/certificates/', payload)
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        return {
            'changed': True,
            'certificate': result['data'],
            'cert_id': result['data']['id'],
            'msg': f"Issued certificate '{cn}' with ID: {result['data']['id']}",
        }

    def cert_list(self, ca_id=None, status=None, cert_type=None):
        """List certificates."""
        params = {}
        if ca_id:
            params['caId'] = ca_id
        if status:
            params['status'] = status
        if cert_type:
            params['type'] = cert_type

        result, items, total = self.get_all('/certificates/', params=params)
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        return {
            'changed': False,
            'certificates': items,
            'cert_count': total,
            'msg': f"Found {total} certificates",
        }

    def cert_get(self, cert_id):
        """Get certificate details."""
        result = self.get(f'/certificates/{cert_id}')
        if result['status'] == 404:
            return {'changed': False, 'failed': True, 'msg': f"Certificate {cert_id} not found"}
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        return {'changed': False, 'certificate': result['data'], 'msg': f"Retrieved certificate {cert_id}"}

    def cert_renew(self, cert_id, validity=365):
        """Renew a certificate."""
        result = self.post(f'/certificates/{cert_id}/renew', {'validityDays': validity})
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        return {
            'changed': True,
            'certificate': result['data'],
            'new_cert_id': result['data']['id'],
            'msg': f"Certificate renewed, new ID: {result['data']['id']}",
        }

    def cert_revoke(self, cert_id, reason='unspecified', details=None):
        """Revoke a certificate."""
        payload = {'reason': reason}
        if details:
            payload['details'] = details
        result = self.post(f'/certificates/{cert_id}/revoke', payload)
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        return {'changed': True, 'msg': f"Certificate {cert_id} revoked with reason: {reason}"}

    def cert_delete(self, cert_id):
        """Delete a certificate."""
        result = self.delete(f'/certificates/{cert_id}')
        if result['status'] == 404:
            return {'changed': False, 'msg': f"Certificate {cert_id} not found (already deleted?)"}
        if result['status'] == 409:
            return {'changed': False,
                    'msg': f"Certificate {cert_id} cannot be deleted yet: {result['error']}"}
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        return {'changed': True, 'msg': f"Certificate {cert_id} deleted"}

    def cert_find(self, cert_pem):
        """Find the certificate whose serial is the serial of cert_pem."""
        try:
            from cryptography import x509
        except ImportError:
            return {'changed': False, 'failed': True,
                    'msg': 'cert_find needs the Python cryptography library where the module runs'}
        try:
            cert = x509.load_pem_x509_certificate(cert_pem.strip().encode('utf-8'))
        except ValueError as e:
            return {'changed': False, 'failed': True, 'msg': f"cert_pem is not a PEM certificate: {e}"}
        serial = format(cert.serial_number, 'x')
        result = self.get('/certificates/', params={'search': serial, 'limit': 100})
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        norm = serial.lstrip('0').lower()
        for item in (result['data'] or {}).get('items', []):
            if str(item.get('serialNumber', '')).lstrip('0').lower() == norm:
                return {'changed': False, 'certificate': item, 'cert_id': item['id'],
                        'msg': f"Found certificate {item['id']} with serial {serial}"}
        return {'changed': False, 'failed': True, 'serial_number': serial,
                'msg': f"No certificate with serial {serial} on the server"}

    def cert_download(self, cert_id, format='pem', password=None, dest=None):
        """Download a certificate."""
        params = {'format': format}
        headers = None
        if password and format in ['p12', 'pfx', 'jks-keystore', 'jks-truststore', 'pkcs8-encrypted']:
            # A header, never the query string: URLs end up in server and proxy logs.
            headers = {'X-Export-Password': password}

        result = self.get(f'/certificates/{cert_id}/download', params=params, extra_headers=headers)
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}

        data = result['data']
        content = base64.b64decode(data.get('data', ''))
        filename = data.get('filename', f'{cert_id}.{format}')

        if dest:
            try:
                if os.path.isfile(dest) and not os.path.islink(dest):
                    with open(dest, 'rb') as f:
                        same = f.read() == content
                    if same and (os.stat(dest).st_mode & 0o777) == 0o600:
                        return {'changed': False, 'downloaded_file': dest, 'filename': filename,
                                'msg': f"{dest} is up to date"}
                if self.module.check_mode:
                    return {'changed': True, 'downloaded_file': dest, 'filename': filename,
                            'msg': f"{dest} would be written (check mode)"}
                # Write a 0600 temp file in the same directory, then rename: no
                # moment with the content in a file that others can read.
                fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(dest)), prefix='.pki-')
                try:
                    with os.fdopen(fd, 'wb') as f:
                        f.write(content)
                    os.replace(tmp, dest)
                except BaseException:
                    if os.path.exists(tmp):
                        os.unlink(tmp)
                    raise
                return {
                    'changed': True,
                    'downloaded_file': dest,
                    'filename': filename,
                    'msg': f"Certificate downloaded to {dest}",
                }
            except IOError as e:
                return {'changed': False, 'failed': True, 'msg': f"Failed to write file: {e}"}

        return {
            'changed': False,
            'content': base64.b64encode(content).decode('utf-8'),
            'filename': filename,
            'msg': f"Certificate {cert_id} downloaded as {format}",
        }

    # ========================= SSH workflow helpers =========================
    def _origin(self):
        """Return the server origin (api_url minus the /api/v1 suffix).

        The SSH surface spans prefixes off one host: /api/v1/ssh (admin REST),
        /api/v1/external/ssh (fleet-token host REST), and root-level public
        downloads (/ssh/cert-authority, /ssh/trusted-user-ca-keys, ...). All
        REST — no tRPC.
        """
        u = self.api_url
        for suffix in ('/api/v1', '/api'):
            if u.endswith(suffix):
                return u[:-len(suffix)]
        return u

    def _get_text(self, path):
        """GET a root-level text/plain resource (e.g. /ssh/cert-authority)."""
        url = f"{self._origin()}{path}"
        headers = {}
        if self.access_token:
            headers['Authorization'] = f"Bearer {self.access_token}"
        try:
            resp = self._open(url, headers=headers, method='GET')
            return {'status': resp.getcode(), 'text': resp.read().decode('utf-8'), 'error': None}
        except Exception as e:
            err = self._err(e)
            return {'status': err['status'], 'text': None, 'error': err['error']}

    def _fleet_request(self, method, endpoint, data=None, extra_headers=None):
        """Request the host-facing external API with the fleet bearer token."""
        if not self.fleet_token:
            return {'status': 400, 'data': None, 'error': 'fleet_token is required for host-facing SSH actions'}
        url = f"{self.api_url}{endpoint}"
        headers = {'Authorization': f"Bearer {self.fleet_token}"}
        if extra_headers:
            headers.update(extra_headers)
        body = None
        if data is not None:
            headers['Content-Type'] = 'application/json'
            body = json.dumps(data)
        try:
            resp = self._open(url, data=body, headers=headers, method=method)
            try:
                return {'status': resp.getcode(), 'data': json.loads(resp.read()), 'error': None}
            except (json.JSONDecodeError, ValueError):
                return {'status': resp.getcode(), 'data': None, 'error': None}
        except Exception as e:
            return self._err(e)

    # ============================ SSH zones ============================
    def zone_id(self, zone):
        """Resolve a zone id or name to its id (the list filters need the id)."""
        r = self.get(f"/ssh/zones/{quote(zone, safe='')}")
        if r['error']:
            self.module.fail_json(msg=f"SSH zone '{zone}' not found: {r['error']}")
        return r['data']['id']

    def ssh_zone_list(self):
        r = self.get('/ssh/zones')
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        zones = r['data'] if isinstance(r['data'], list) else (r['data'] or {}).get('items', [])
        return {'changed': False, 'ssh_zones': zones, 'msg': f"Found {len(zones)} SSH zones"}

    def ssh_zone_create(self, name, display_name=None, description=None):
        r = self.get(f"/ssh/zones/{quote(name, safe='')}")
        if not r['error']:
            return {'changed': False, 'ssh_zone': r['data'], 'zone_id': r['data']['id'],
                    'msg': f"SSH zone {name} exists"}
        payload = {'name': name, 'displayName': display_name or name}
        if description:
            payload['description'] = description
        r = self.post('/ssh/zones', payload)
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': True, 'ssh_zone': r['data'], 'zone_id': r['data']['id'],
                'msg': f"Created SSH zone {name}"}

    @staticmethod
    def _zone_path(path, zone):
        """The zone-scoped public trust URL, or the old default-zone URL."""
        if not zone:
            return path
        return path.replace('/ssh/', f"/ssh/zones/{quote(zone, safe='')}/", 1)

    @staticmethod
    def _trust_error(r, zone):
        msg = r['error']
        if zone and r['status'] == 404:
            msg = f"SSH zone '{zone}' not found"
        return {'changed': False, 'failed': True, 'msg': msg}

    # ===================== SSH admin / operator actions =====================
    def ssh_ca_create(self, ca_type, label=None, zone=None):
        payload = {'caType': ca_type}
        if label:
            payload['label'] = label
        if zone:
            payload['zone'] = zone
        r = self.post('/ssh/cas', payload)
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': True, 'ssh_ca': r['data'], 'ca_id': r['data']['id'],
                'msg': f"Created SSH {ca_type} CA {r['data']['id']}"}

    def ssh_ca_list(self, zone=None):
        r = self.get('/ssh/cas', params={'zoneId': self.zone_id(zone)} if zone else None)
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': False, 'ssh_cas': r['data'], 'msg': f"Found {len(r['data'])} SSH CAs"}

    def ssh_token_mint(self, name, host_ca_id=None, user_ca_id=None, ops=None, zone=None):
        payload = {'name': name, 'opSet': ops or []}
        if zone:
            payload['zone'] = zone
        if host_ca_id:
            payload['hostCaId'] = host_ca_id
        if user_ca_id:
            payload['userCaId'] = user_ca_id
        r = self.post('/ssh/tokens', payload)
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': True, 'token': r['data']['token'], 'ssh_token': r['data']['record'],
                'msg': f"Minted fleet token {r['data']['record']['id']}"}

    def ssh_identity_create(self, subject, email=None, external_subject=None, zone=None):
        payload = {'subject': subject}
        if zone:
            payload['zone'] = zone
        if email:
            payload['email'] = email
        if external_subject:
            payload['externalSubject'] = external_subject
        r = self.post('/ssh/identities', payload)
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': True, 'ssh_identity': r['data'], 'identity_id': r['data']['id'],
                'msg': f"Created SSH identity {subject}"}

    def ssh_principal_create(self, name, description=None, zone=None):
        payload = {'name': name}
        if zone:
            payload['zone'] = zone
        if description:
            payload['description'] = description
        r = self.post('/ssh/principals', payload)
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': True, 'ssh_principal': r['data'], 'principal_id': r['data']['id'],
                'msg': f"Created SSH principal {name}"}

    def ssh_principal_grant(self, identity_id, principal_id):
        r = self.post('/ssh/principals/grant', {'identityId': identity_id, 'principalId': principal_id})
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': True, 'msg': f"Granted principal {principal_id} to identity {identity_id}"}

    def ssh_principal_map(self, host_id, principal_id, local_account):
        r = self.post('/ssh/principals/map', {'hostId': host_id, 'principalId': principal_id, 'localAccount': local_account})
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': True, 'msg': f"Mapped principal {principal_id} -> {local_account} on host {host_id}"}

    def ssh_user_issue(self, identity_id, ssh_public_key, principals, ca_id=None,
                       valid_for_seconds=None, enforce_entitlement=None):
        payload = {'identityId': identity_id, 'sshPublicKey': ssh_public_key, 'principals': principals}
        if ca_id:
            payload['caId'] = ca_id
        if valid_for_seconds:
            payload['validForSeconds'] = valid_for_seconds
        if enforce_entitlement is not None:
            payload['enforceEntitlement'] = enforce_entitlement
        r = self.post('/ssh/users/issue', payload)
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        cert = r['data'].get('cert', r['data'])
        return {'changed': True, 'ssh_certificate': r['data'], 'cert_openssh': cert.get('certOpenssh'),
                'msg': f"Issued SSH user cert for identity {identity_id}"}

    def ssh_host_register(self, fqdn, ssh_public_key, addresses=None, zone=None):
        payload = {'fqdn': fqdn, 'opensshHostPubkey': ssh_public_key, 'addresses': addresses or []}
        if zone:
            payload['zone'] = zone
        r = self.post('/ssh/hosts', payload)
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': True, 'ssh_host': r['data'], 'host_id': r['data']['id'],
                'msg': f"Registered SSH host {fqdn}"}

    def ssh_host_list(self, fqdn=None, zone=None):
        params = {}
        if fqdn:
            params['fqdn'] = fqdn
        if zone:
            params['zoneId'] = self.zone_id(zone)
        r = self.get('/ssh/hosts', params=params or None)
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        hosts = r['data'] or []
        if fqdn:
            return {'changed': False, 'ssh_hosts': hosts,
                    'host_id': (hosts[0]['id'] if hosts else None),
                    'msg': (f"Resolved host {fqdn}" if hosts else f"Host {fqdn} not found")}
        return {'changed': False, 'ssh_hosts': hosts, 'msg': f"Found {len(hosts)} SSH hosts"}

    def ssh_block(self, host_id, identity_id, reason=None):
        payload = {'hostId': host_id, 'identityId': identity_id}
        if reason:
            payload['reason'] = reason
        r = self.post('/ssh/blocks', payload)
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': True, 'ssh_block': r['data'],
                'msg': f"Blocked identity {identity_id} on host {host_id}"}

    def ssh_unblock(self, host_id, identity_id):
        r = self.post('/ssh/blocks/unblock', {'hostId': host_id, 'identityId': identity_id})
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': True, 'msg': f"Unblocked identity {identity_id} on host {host_id}"}

    def ssh_auth_principals(self, host_id):
        r = self.get(f'/ssh/hosts/{host_id}/auth-principals')
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': False, 'auth_principals': r['data'],
                'msg': f"Rendered auth_principals for host {host_id}"}

    def ssh_sshd_config(self, host_id):
        """The authoritative, algorithm-aware sshd drop-in for a host."""
        r = self._get_text(f"/ssh/hosts/{host_id}/sshd-config")
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': False, 'sshd_config': r['text'],
                'msg': f"Rendered sshd drop-in for host {host_id}"}

    def ssh_cert_authority(self, pattern='*', zone=None):
        r = self._get_text(self._zone_path(f"/ssh/cert-authority?pattern={quote(pattern)}", zone))
        if r['error']:
            return self._trust_error(r, zone)
        return {'changed': False, 'cert_authority': (r['text'] or '').strip(),
                'msg': "Fetched @cert-authority line"}

    def ssh_trusted_user_ca(self, zone=None):
        r = self._get_text(self._zone_path('/ssh/trusted-user-ca-keys', zone))
        if r['error']:
            return self._trust_error(r, zone)
        return {'changed': False, 'trusted_user_ca_keys': r['text'], 'msg': "Fetched TrustedUserCAKeys"}

    def ssh_host_ca(self, zone=None):
        r = self._get_text(self._zone_path('/ssh/host-ca-keys', zone))
        if r['error']:
            return self._trust_error(r, zone)
        return {'changed': False, 'host_ca_keys': r['text'], 'msg': "Fetched Host-CA trust anchor"}

    # =================== SSH host-facing actions (fleet token) ==============
    def ssh_sign_host(self, fqdn, ssh_public_key, addresses=None,
                      idempotency_key=None, valid_for_seconds=None, key_id=None):
        payload = {'fqdn': fqdn, 'opensshHostPubkey': ssh_public_key, 'addresses': addresses or []}
        if valid_for_seconds:
            payload['validForSeconds'] = valid_for_seconds
        if key_id:
            payload['keyId'] = key_id
        extra = {'Idempotency-Key': idempotency_key} if idempotency_key else None
        r = self._fleet_request('POST', '/external/ssh/sign-host', payload, extra)
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': True, 'ssh_host_cert': r['data'],
                'host_id': (r['data'] or {}).get('hostId'),
                'cert_openssh': (r['data'] or {}).get('certOpenssh'),
                'msg': f"Signed host cert for {fqdn}"}

    def ssh_register_host_pubkey(self, fqdn):
        r = self._fleet_request('POST', '/external/ssh/register-host-pubkey', {'fqdn': fqdn})
        if r['status'] == 501:
            return {'changed': False, 'failed': True,
                    'msg': 'ECIES KRL path disabled on the backend (set SSH_ECIES_ENABLED=true)'}
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': True, 'msg': f"Registered ECIES key for {fqdn}"}

    def ssh_get_principals(self, fqdn):
        r = self._fleet_request('GET', f'/external/ssh/hosts/{fqdn}/auth-principals')
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        return {'changed': False, 'auth_principals': r['data'],
                'msg': f"Fetched auth_principals for {fqdn}"}

    def ssh_principals_pushed(self, fqdn, sha256):
        """Acknowledge that the principal files were installed (marks the host not stale)."""
        r = self._fleet_request('POST', f'/external/ssh/hosts/{fqdn}/principals-pushed', {'sha256': sha256})
        if r['status'] == 409 and isinstance(r.get('body'), dict):
            code = (r['body'].get('error') or {}).get('code')
            if code == 'SHA256_MISMATCH':
                return {'changed': False, 'failed': True, 'sha256_mismatch': True,
                        'current_sha256': r['body'].get('currentSha256'),
                        'msg': f"SHA256_MISMATCH for {fqdn}: the principal mappings changed after the fetch "
                               "(fetch and install again, then acknowledge)"}
        if r['error']:
            return {'changed': False, 'failed': True, 'msg': r['error']}
        data = r['data'] or {}
        return {'changed': True, 'principals_pushed': data,
                'last_principal_push_at': data.get('lastPrincipalPushAt'),
                'msg': f"Acknowledged principal push for {fqdn}"}


def run_module():
    """Run the Ansible module."""
    module_args = dict(
        action=dict(type='str', required=True, choices=[
            'auth_test', 'stats', 'expiring', 'search',
            'ca_create', 'ca_list', 'ca_get', 'ca_revoke', 'ca_delete',
            'cert_issue', 'cert_list', 'cert_get', 'cert_renew', 'cert_revoke', 'cert_delete', 'cert_download',
            'cert_find',
            # SSH workflow — admin/operator (OIDC or unauthenticated)
            'ssh_ca_create', 'ssh_ca_list', 'ssh_token_mint',
            'ssh_identity_create', 'ssh_principal_create', 'ssh_principal_grant', 'ssh_principal_map',
            'ssh_user_issue', 'ssh_host_register', 'ssh_host_list',
            'ssh_block', 'ssh_unblock', 'ssh_auth_principals', 'ssh_sshd_config',
            'ssh_cert_authority', 'ssh_trusted_user_ca', 'ssh_host_ca',
            # SSH workflow — host-facing (fleet-token)
            'ssh_sign_host', 'ssh_register_host_pubkey', 'ssh_get_principals',
            'ssh_principals_pushed',
            # SSH zones
            'ssh_zone_list', 'ssh_zone_create',
        ]),
        api_url=dict(type='str', required=True),
        # OIDC is optional: omit for a backend with OIDC disabled
        # (ALLOW_UNAUTHENTICATED_SSH_CA=true) or for fleet-token host actions.
        oidc_url=dict(type='str'),
        client_id=dict(type='str'),
        client_secret=dict(type='str', no_log=True),
        api_token=dict(type='str', no_log=True),
        ca_path=dict(type='path'),
        # CA options
        ca_id=dict(type='str'),
        ca_cn=dict(type='str'),
        ca_org=dict(type='str'),
        ca_country=dict(type='str'),
        ca_ou=dict(type='str'),
        ca_state=dict(type='str'),
        ca_locality=dict(type='str'),
        ca_algorithm=dict(type='str', default='RSA-4096', choices=['RSA-2048', 'RSA-4096']),
        ca_validity_years=dict(type='int'),
        ca_validity=dict(type='int'),
        # Certificate options
        cert_id=dict(type='str'),
        cert_cn=dict(type='str'),
        cert_org=dict(type='str'),
        cert_country=dict(type='str'),
        cert_ou=dict(type='str'),
        cert_state=dict(type='str'),
        cert_locality=dict(type='str'),
        cert_type=dict(type='str', choices=['server', 'client', 'dual', 'email', 'code_signing']),
        cert_status=dict(type='str', choices=['active', 'revoked', 'expired']),
        cert_algorithm=dict(type='str', default='RSA-2048', choices=['RSA-2048', 'RSA-4096', 'ECDSA-P256', 'ECDSA-P384']),
        cert_validity=dict(type='int', default=365),
        cert_dns_names=dict(type='list', elements='str'),
        cert_ip_addresses=dict(type='list', elements='str'),
        cert_emails=dict(type='list', elements='str'),
        # Revocation
        revocation_reason=dict(type='str', default='unspecified', choices=[
            'unspecified', 'keyCompromise', 'caCompromise', 'affiliationChanged',
            'superseded', 'cessationOfOperation', 'certificateHold', 'removeFromCRL',
        ]),
        revocation_details=dict(type='str'),
        cert_pem=dict(type='str'),
        # Download
        download_format=dict(type='str', default='pem', choices=[
            'pem', 'der', 'chain-pem', 'full-pem', 'full-der', 'key-pem', 'key-der',
            'csr-pem', 'p12', 'pfx', 'pkcs8-pem', 'pkcs8-der', 'pkcs8-encrypted',
            'jks-keystore', 'jks-truststore',
        ]),
        download_password=dict(type='str', no_log=True),
        download_dest=dict(type='path'),
        # Search
        search_query=dict(type='str'),
        search_limit=dict(type='int', default=10),
        expiring_limit=dict(type='int', default=5),
        # SSH workflow
        ssh_ca_type=dict(type='str', choices=['user', 'host']),
        ssh_ca_label=dict(type='str'),
        token_name=dict(type='str'),
        token_ops=dict(type='list', elements='str'),
        host_ca_id=dict(type='str'),
        user_ca_id=dict(type='str'),
        identity_id=dict(type='str'),
        identity_subject=dict(type='str'),
        identity_email=dict(type='str'),
        principal_id=dict(type='str'),
        principal_name=dict(type='str'),
        principal_description=dict(type='str'),
        host_id=dict(type='str'),
        host_fqdn=dict(type='str'),
        principals_sha256=dict(type='str'),
        host_pubkey=dict(type='str'),
        host_addresses=dict(type='list', elements='str'),
        local_account=dict(type='str'),
        ssh_public_key=dict(type='str'),
        principals=dict(type='list', elements='str'),
        user_valid_seconds=dict(type='int'),
        host_valid_seconds=dict(type='int'),
        host_key_id=dict(type='str'),
        identity_external_subject=dict(type='str'),
        enforce_entitlement=dict(type='bool'),
        cert_authority_pattern=dict(type='str', default='*'),
        block_reason=dict(type='str'),
        idempotency_key=dict(type='str'),
        fleet_token=dict(type='str', no_log=True),
        zone=dict(type='str'),
        zone_display_name=dict(type='str'),
        zone_description=dict(type='str'),
        # Connection
        validate_certs=dict(type='bool', default=True),
        timeout=dict(type='int', default=30),
        token_cache_path=dict(type='path', no_log=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[('ca_validity_years', 'ca_validity')],
        required_if=[
            ('action', 'ca_create', ['ca_cn', 'ca_org', 'ca_country']),
            ('action', 'ca_get', ['ca_id']),
            ('action', 'ca_revoke', ['ca_id']),
            ('action', 'ca_delete', ['ca_id']),
            ('action', 'cert_issue', ['ca_id', 'cert_cn', 'cert_org', 'cert_country']),
            ('action', 'cert_get', ['cert_id']),
            ('action', 'cert_renew', ['cert_id']),
            ('action', 'cert_revoke', ['cert_id']),
            ('action', 'cert_delete', ['cert_id']),
            ('action', 'cert_download', ['cert_id']),
            ('action', 'cert_find', ['cert_pem']),
            ('action', 'search', ['search_query']),
            # SSH workflow
            ('action', 'ssh_ca_create', ['ssh_ca_type']),
            ('action', 'ssh_token_mint', ['token_name', 'token_ops']),
            ('action', 'ssh_identity_create', ['identity_subject']),
            ('action', 'ssh_principal_create', ['principal_name']),
            ('action', 'ssh_principal_grant', ['identity_id', 'principal_id']),
            ('action', 'ssh_principal_map', ['host_id', 'principal_id', 'local_account']),
            ('action', 'ssh_user_issue', ['identity_id', 'ssh_public_key', 'principals']),
            ('action', 'ssh_host_register', ['host_fqdn', 'host_pubkey']),
            ('action', 'ssh_block', ['host_id', 'identity_id']),
            ('action', 'ssh_unblock', ['host_id', 'identity_id']),
            ('action', 'ssh_auth_principals', ['host_id']),
            ('action', 'ssh_sshd_config', ['host_id']),
            ('action', 'ssh_sign_host', ['host_fqdn', 'host_pubkey', 'fleet_token']),
            ('action', 'ssh_register_host_pubkey', ['host_fqdn', 'fleet_token']),
            ('action', 'ssh_get_principals', ['host_fqdn', 'fleet_token']),
            ('action', 'ssh_principals_pushed', ['host_fqdn', 'fleet_token', 'principals_sha256']),
            ('action', 'ssh_zone_create', ['zone']),
        ],
    )

    action = module.params['action']

    # Create client
    client = PKIManagerClient(
        module=module,
        api_url=module.params['api_url'],
        oidc_url=module.params['oidc_url'],
        client_id=module.params['client_id'],
        client_secret=module.params['client_secret'],
        validate_certs=module.params['validate_certs'],
        timeout=module.params['timeout'],
        token_cache_path=module.params['token_cache_path'],
        fleet_token=module.params.get('fleet_token'),
        api_token=module.params.get('api_token'),
        ca_path=module.params.get('ca_path'),
    )

    # Authenticate (OIDC; no-op when no client credentials are supplied)
    client.authenticate()

    # Execute action
    result = {}

    if action == 'auth_test':
        result = client.auth_test()

    elif action == 'stats':
        result = client.stats()

    elif action == 'expiring':
        result = client.expiring(limit=module.params['expiring_limit'])

    elif action == 'search':
        result = client.search(
            query=module.params['search_query'],
            limit=module.params['search_limit'],
        )

    elif action == 'ca_create':
        validity_years = module.params['ca_validity_years']
        if module.params['ca_validity'] is not None:
            # The API takes years; the old option was days and the server ignored it.
            validity_years = max(1, min(30, int(round(module.params['ca_validity'] / 365.0))))
            module.deprecate(
                'ca_validity (days) is deprecated; use ca_validity_years. '
                f"Sending validityYears={validity_years}.",
                version='4.0.0', collection_name='oriolrius.pki_manager')
        if validity_years is not None and not 1 <= validity_years <= 30:
            module.fail_json(msg='ca_validity_years must be between 1 and 30')
        if module.check_mode:
            result = {'changed': True, 'msg': 'CA would be created (check mode)'}
        else:
            result = client.ca_create(
                cn=module.params['ca_cn'],
                org=module.params['ca_org'],
                country=module.params['ca_country'],
                ou=module.params['ca_ou'],
                state=module.params['ca_state'],
                locality=module.params['ca_locality'],
                algorithm=module.params['ca_algorithm'],
                validity_years=validity_years,
            )

    elif action == 'ca_list':
        result = client.ca_list()

    elif action == 'ca_get':
        result = client.ca_get(ca_id=module.params['ca_id'])

    elif action == 'ca_revoke':
        if module.check_mode:
            result = {'changed': True, 'msg': 'CA would be revoked (check mode)'}
        else:
            result = client.ca_revoke(
                ca_id=module.params['ca_id'],
                reason=module.params['revocation_reason'],
                details=module.params.get('revocation_details'),
            )

    elif action == 'ca_delete':
        if module.check_mode:
            result = {'changed': True, 'msg': 'CA would be deleted (check mode)'}
        else:
            result = client.ca_delete(ca_id=module.params['ca_id'])

    elif action == 'cert_issue':
        if module.check_mode:
            result = {'changed': True, 'msg': 'Certificate would be issued (check mode)'}
        else:
            result = client.cert_issue(
                ca_id=module.params['ca_id'],
                cn=module.params['cert_cn'],
                org=module.params['cert_org'],
                country=module.params['cert_country'],
                ou=module.params['cert_ou'],
                state=module.params['cert_state'],
                locality=module.params['cert_locality'],
                cert_type=module.params['cert_type'],
                algorithm=module.params['cert_algorithm'],
                validity=module.params['cert_validity'],
                dns_names=module.params['cert_dns_names'],
                ip_addresses=module.params['cert_ip_addresses'],
                emails=module.params['cert_emails'],
            )

    elif action == 'cert_list':
        result = client.cert_list(
            ca_id=module.params.get('ca_id'),
            status=module.params.get('cert_status'),
            cert_type=module.params.get('cert_type'),
        )

    elif action == 'cert_find':
        result = client.cert_find(module.params['cert_pem'])

    elif action == 'cert_get':
        result = client.cert_get(cert_id=module.params['cert_id'])

    elif action == 'cert_renew':
        if module.check_mode:
            result = {'changed': True, 'msg': 'Certificate would be renewed (check mode)'}
        else:
            result = client.cert_renew(
                cert_id=module.params['cert_id'],
                validity=module.params['cert_validity'],
            )

    elif action == 'cert_revoke':
        if module.check_mode:
            result = {'changed': True, 'msg': 'Certificate would be revoked (check mode)'}
        else:
            result = client.cert_revoke(
                cert_id=module.params['cert_id'],
                reason=module.params['revocation_reason'],
                details=module.params.get('revocation_details'),
            )

    elif action == 'cert_delete':
        if module.check_mode:
            result = {'changed': True, 'msg': 'Certificate would be deleted (check mode)'}
        else:
            result = client.cert_delete(cert_id=module.params['cert_id'])

    elif action == 'cert_download':
        # Validate password for encrypted formats
        fmt = module.params['download_format']
        if fmt in ['p12', 'pfx', 'jks-keystore', 'jks-truststore', 'pkcs8-encrypted']:
            if not module.params.get('download_password'):
                module.fail_json(msg=f"download_password is required for {fmt} format")

        if module.check_mode and not module.params.get('download_dest'):
            result = {'changed': False, 'msg': 'Certificate would be downloaded (check mode)'}
        else:
            # With download_dest, check mode compares the file and reports a change only when needed.
            result = client.cert_download(
                cert_id=module.params['cert_id'],
                format=fmt,
                password=module.params.get('download_password'),
                dest=module.params.get('download_dest'),
            )

    # ---- SSH workflow actions ----
    elif action == 'ssh_ca_create':
        if module.check_mode:
            result = {'changed': True, 'msg': 'SSH CA would be created (check mode)'}
        else:
            result = client.ssh_ca_create(module.params['ssh_ca_type'], module.params.get('ssh_ca_label'), module.params.get('zone'))

    elif action == 'ssh_ca_list':
        result = client.ssh_ca_list(module.params.get('zone'))

    elif action == 'ssh_token_mint':
        if module.check_mode:
            result = {'changed': True, 'msg': 'Fleet token would be minted (check mode)'}
        else:
            result = client.ssh_token_mint(
                name=module.params['token_name'],
                host_ca_id=module.params.get('host_ca_id'),
                user_ca_id=module.params.get('user_ca_id'),
                ops=module.params.get('token_ops'),
                zone=module.params.get('zone'),
            )

    elif action == 'ssh_identity_create':
        if module.check_mode:
            result = {'changed': True, 'msg': 'SSH identity would be created (check mode)'}
        else:
            result = client.ssh_identity_create(
                module.params['identity_subject'],
                module.params.get('identity_email'),
                module.params.get('identity_external_subject'),
                module.params.get('zone'),
            )

    elif action == 'ssh_principal_create':
        if module.check_mode:
            result = {'changed': True, 'msg': 'SSH principal would be created (check mode)'}
        else:
            result = client.ssh_principal_create(module.params['principal_name'], module.params.get('principal_description'), module.params.get('zone'))

    elif action == 'ssh_principal_grant':
        if module.check_mode:
            result = {'changed': True, 'msg': 'Entitlement would be granted (check mode)'}
        else:
            result = client.ssh_principal_grant(module.params['identity_id'], module.params['principal_id'])

    elif action == 'ssh_principal_map':
        if module.check_mode:
            result = {'changed': True, 'msg': 'Principal would be mapped (check mode)'}
        else:
            result = client.ssh_principal_map(module.params['host_id'], module.params['principal_id'], module.params['local_account'])

    elif action == 'ssh_user_issue':
        if module.check_mode:
            result = {'changed': True, 'msg': 'SSH user cert would be issued (check mode)'}
        else:
            result = client.ssh_user_issue(
                identity_id=module.params['identity_id'],
                ssh_public_key=module.params['ssh_public_key'],
                principals=module.params['principals'],
                ca_id=module.params.get('user_ca_id'),
                valid_for_seconds=module.params.get('user_valid_seconds'),
                enforce_entitlement=module.params.get('enforce_entitlement'),
            )

    elif action == 'ssh_host_register':
        if module.check_mode:
            result = {'changed': True, 'msg': 'SSH host would be registered (check mode)'}
        else:
            result = client.ssh_host_register(module.params['host_fqdn'], module.params['host_pubkey'],
                                              module.params.get('host_addresses'), module.params.get('zone'))

    elif action == 'ssh_host_list':
        result = client.ssh_host_list(module.params.get('host_fqdn'), module.params.get('zone'))

    elif action == 'ssh_block':
        if module.check_mode:
            result = {'changed': True, 'msg': 'Identity would be blocked (check mode)'}
        else:
            result = client.ssh_block(module.params['host_id'], module.params['identity_id'], module.params.get('block_reason'))

    elif action == 'ssh_unblock':
        if module.check_mode:
            result = {'changed': True, 'msg': 'Identity would be unblocked (check mode)'}
        else:
            result = client.ssh_unblock(module.params['host_id'], module.params['identity_id'])

    elif action == 'ssh_auth_principals':
        result = client.ssh_auth_principals(module.params['host_id'])

    elif action == 'ssh_sshd_config':
        result = client.ssh_sshd_config(module.params['host_id'])

    elif action == 'ssh_cert_authority':
        result = client.ssh_cert_authority(module.params.get('cert_authority_pattern', '*'), module.params.get('zone'))

    elif action == 'ssh_trusted_user_ca':
        result = client.ssh_trusted_user_ca(module.params.get('zone'))

    elif action == 'ssh_host_ca':
        result = client.ssh_host_ca(module.params.get('zone'))

    elif action == 'ssh_sign_host':
        if module.check_mode:
            result = {'changed': True, 'msg': 'Host cert would be signed (check mode)'}
        else:
            result = client.ssh_sign_host(
                fqdn=module.params['host_fqdn'],
                ssh_public_key=module.params['host_pubkey'],
                addresses=module.params.get('host_addresses'),
                idempotency_key=module.params.get('idempotency_key'),
                valid_for_seconds=(module.params.get('host_valid_seconds')
                                   or module.params.get('user_valid_seconds')),
                key_id=module.params.get('host_key_id'),
            )

    elif action == 'ssh_register_host_pubkey':
        if module.check_mode:
            result = {'changed': True, 'msg': 'ECIES key would be registered (check mode)'}
        else:
            result = client.ssh_register_host_pubkey(module.params['host_fqdn'])

    elif action == 'ssh_get_principals':
        result = client.ssh_get_principals(module.params['host_fqdn'])

    elif action == 'ssh_principals_pushed':
        if module.check_mode:
            result = {'changed': True, 'msg': 'Principal push would be acknowledged (check mode)'}
        else:
            result = client.ssh_principals_pushed(module.params['host_fqdn'], module.params['principals_sha256'])

    elif action == 'ssh_zone_list':
        result = client.ssh_zone_list()

    elif action == 'ssh_zone_create':
        if module.check_mode:
            result = {'changed': True, 'msg': 'SSH zone would be created (check mode)'}
        else:
            result = client.ssh_zone_create(module.params['zone'], module.params.get('zone_display_name'),
                                            module.params.get('zone_description'))

    # Return result
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
