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
    api_url:
        description:
            - PKI Manager API URL.
        required: true
        type: str
    oidc_url:
        description:
            - OIDC token endpoint URL.
        required: true
        type: str
    client_id:
        description:
            - OIDC client ID.
        required: true
        type: str
    client_secret:
        description:
            - OIDC client secret.
        required: true
        type: str
        no_log: true
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
            - Key algorithm for CA.
        type: str
        choices: ['RSA-2048', 'RSA-4096', 'ECDSA-P256', 'ECDSA-P384']
        default: 'RSA-4096'
    ca_validity:
        description:
            - CA validity in days.
        type: int
        default: 3650
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
            - Certificate Organization.
        type: str
    cert_country:
        description:
            - Certificate Country code (2 letters).
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
            - Certificate type.
        type: str
        choices: ['server', 'client', 'email', 'code_signing']
        default: 'server'
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
            - privilegeWithdrawn
            - aaCompromise
        default: 'unspecified'
    download_format:
        description:
            - Certificate download format.
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
        type: str
        no_log: true
    download_dest:
        description:
            - Destination path for downloaded certificate.
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
            - Path to cache OIDC tokens.
        type: path
        default: '/tmp/.pki_token_cache'
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
    ca_validity: 3650
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
msg:
    description: Status message.
    type: str
    returned: always
'''

import json
import os
import time
import base64
import ssl
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url

try:
    from urllib.parse import urlencode, quote
except ImportError:
    from urllib import urlencode, quote


class PKIManagerClient:
    """Client for PKI Manager API operations."""

    def __init__(self, module, api_url, oidc_url, client_id, client_secret,
                 validate_certs=True, timeout=30, token_cache_path='/tmp/.pki_token_cache'):
        self.module = module
        self.api_url = api_url.rstrip('/')
        self.oidc_url = oidc_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.validate_certs = validate_certs
        self.timeout = timeout
        self.token_cache_path = token_cache_path
        self.access_token = None

    def authenticate(self):
        """Authenticate with OIDC and get access token."""
        # Try to use cached token
        if self._load_cached_token():
            return True

        # Request new token
        data = urlencode({
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        })

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            response = open_url(
                self.oidc_url,
                data=data,
                headers=headers,
                method='POST',
                timeout=self.timeout,
                validate_certs=self.validate_certs,
            )
            token_data = json.loads(response.read())
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 300)
            self._cache_token(expires_in)
            return True
        except Exception as e:
            self.module.fail_json(msg=f"OIDC authentication failed: {e}")

    def _load_cached_token(self):
        """Load token from cache if valid."""
        try:
            if os.path.exists(self.token_cache_path):
                with open(self.token_cache_path, 'r') as f:
                    cache = json.load(f)
                if cache.get('expires_at', 0) > time.time() + 60:  # 60s buffer
                    self.access_token = cache['access_token']
                    return True
        except (IOError, json.JSONDecodeError):
            pass
        return False

    def _cache_token(self, expires_in):
        """Cache token to file."""
        try:
            cache = {
                'access_token': self.access_token,
                'expires_at': time.time() + expires_in,
            }
            with open(self.token_cache_path, 'w') as f:
                os.chmod(self.token_cache_path, 0o600)
                json.dump(cache, f)
        except IOError:
            pass  # Caching is optional

    def _request(self, method, endpoint, data=None, params=None):
        """Make authenticated API request."""
        url = f"{self.api_url}{endpoint}"
        if params:
            url = f"{url}?{urlencode(params)}"

        headers = {
            'Authorization': f"Bearer {self.access_token}",
        }

        body = None
        if data is not None:
            headers['Content-Type'] = 'application/json'
            body = json.dumps(data)

        try:
            response = open_url(
                url,
                data=body,
                headers=headers,
                method=method,
                timeout=self.timeout,
                validate_certs=self.validate_certs,
            )
            status = response.getcode()

            # Parse response
            try:
                response_data = json.loads(response.read())
                return {'status': status, 'data': response_data, 'error': None}
            except (json.JSONDecodeError, ValueError):
                return {'status': status, 'data': None, 'error': None}

        except Exception as e:
            # Handle HTTP errors
            error_str = str(e)
            status = 500

            # Try to extract status code from exception
            if hasattr(e, 'code'):
                status = e.code
            elif 'HTTP Error' in error_str:
                try:
                    status = int(error_str.split('HTTP Error ')[1].split(':')[0])
                except (IndexError, ValueError):
                    pass

            # Handle common status codes
            if status == 404:
                return {'status': 404, 'data': None, 'error': 'Not found'}
            if status == 409:
                return {'status': 409, 'data': None, 'error': 'Conflict - operation blocked'}

            # Try to get error message from response body
            error_msg = error_str
            if hasattr(e, 'read'):
                try:
                    error_data = json.loads(e.read())
                    error_msg = error_data.get('error', {}).get('message', error_str)
                except:
                    pass

            return {'status': status, 'data': None, 'error': error_msg}

    def get(self, endpoint, params=None):
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint, data=None):
        return self._request('POST', endpoint, data=data)

    def delete(self, endpoint):
        return self._request('DELETE', endpoint)

    # Action implementations
    def auth_test(self):
        """Test authentication."""
        result = self.get('/health')
        if result['error']:
            return {'changed': False, 'msg': f"Authentication failed: {result['error']}"}
        return {'changed': False, 'msg': 'Authentication successful', 'status': result['data']}

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
                  algorithm='RSA-4096', validity=3650):
        """Create a Certificate Authority."""
        payload = {
            'subject': {
                'commonName': cn,
                'organization': org,
                'country': country,
            },
            'keyAlgorithm': algorithm,
            'validityDays': validity,
        }
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
        result = self.get('/cas/')
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        items = result['data'].get('items', [])
        total = result['data'].get('pagination', {}).get('total', len(items))
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

    def ca_revoke(self, ca_id, reason='unspecified'):
        """Revoke a CA."""
        result = self.post(f'/cas/{ca_id}/revoke', {'reason': reason})
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
                   locality=None, cert_type='server', algorithm='RSA-2048',
                   validity=365, dns_names=None, ip_addresses=None, emails=None):
        """Issue a certificate."""
        payload = {
            'caId': ca_id,
            'subject': {'commonName': cn},
            'certificateType': cert_type,
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

        result = self.get('/certificates/', params=params if params else None)
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        items = result['data'].get('items', [])
        total = result['data'].get('pagination', {}).get('total', len(items))
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

    def cert_revoke(self, cert_id, reason='unspecified'):
        """Revoke a certificate."""
        result = self.post(f'/certificates/{cert_id}/revoke', {'reason': reason})
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        return {'changed': True, 'msg': f"Certificate {cert_id} revoked with reason: {reason}"}

    def cert_delete(self, cert_id):
        """Delete a certificate."""
        result = self.delete(f'/certificates/{cert_id}')
        if result['status'] == 404:
            return {'changed': False, 'msg': f"Certificate {cert_id} not found (already deleted?)"}
        if result['status'] in [409, 500]:
            return {'changed': False, 'msg': f"Certificate {cert_id} cannot be deleted yet"}
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}
        return {'changed': True, 'msg': f"Certificate {cert_id} deleted"}

    def cert_download(self, cert_id, format='pem', password=None, dest=None):
        """Download a certificate."""
        params = {'format': format}
        if password and format in ['p12', 'pfx', 'jks-keystore', 'jks-truststore', 'pkcs8-encrypted']:
            params['password'] = password

        result = self.get(f'/certificates/{cert_id}/download', params=params)
        if result['error']:
            return {'changed': False, 'failed': True, 'msg': result['error']}

        data = result['data']
        content = base64.b64decode(data.get('data', ''))
        filename = data.get('filename', f'{cert_id}.{format}')

        if dest:
            try:
                with open(dest, 'wb') as f:
                    f.write(content)
                os.chmod(dest, 0o600)
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


def run_module():
    """Run the Ansible module."""
    module_args = dict(
        action=dict(type='str', required=True, choices=[
            'auth_test', 'stats', 'expiring', 'search',
            'ca_create', 'ca_list', 'ca_get', 'ca_revoke', 'ca_delete',
            'cert_issue', 'cert_list', 'cert_get', 'cert_renew', 'cert_revoke', 'cert_delete', 'cert_download',
        ]),
        api_url=dict(type='str', required=True),
        oidc_url=dict(type='str', required=True),
        client_id=dict(type='str', required=True),
        client_secret=dict(type='str', required=True, no_log=True),
        # CA options
        ca_id=dict(type='str'),
        ca_cn=dict(type='str'),
        ca_org=dict(type='str'),
        ca_country=dict(type='str'),
        ca_ou=dict(type='str'),
        ca_state=dict(type='str'),
        ca_locality=dict(type='str'),
        ca_algorithm=dict(type='str', default='RSA-4096', choices=['RSA-2048', 'RSA-4096', 'ECDSA-P256', 'ECDSA-P384']),
        ca_validity=dict(type='int', default=3650),
        # Certificate options
        cert_id=dict(type='str'),
        cert_cn=dict(type='str'),
        cert_org=dict(type='str'),
        cert_country=dict(type='str'),
        cert_ou=dict(type='str'),
        cert_state=dict(type='str'),
        cert_locality=dict(type='str'),
        cert_type=dict(type='str', default='server', choices=['server', 'client', 'email', 'code_signing']),
        cert_algorithm=dict(type='str', default='RSA-2048', choices=['RSA-2048', 'RSA-4096', 'ECDSA-P256', 'ECDSA-P384']),
        cert_validity=dict(type='int', default=365),
        cert_dns_names=dict(type='list', elements='str'),
        cert_ip_addresses=dict(type='list', elements='str'),
        cert_emails=dict(type='list', elements='str'),
        # Revocation
        revocation_reason=dict(type='str', default='unspecified', choices=[
            'unspecified', 'keyCompromise', 'caCompromise', 'affiliationChanged',
            'superseded', 'cessationOfOperation', 'certificateHold', 'removeFromCRL',
            'privilegeWithdrawn', 'aaCompromise',
        ]),
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
        # Connection
        validate_certs=dict(type='bool', default=True),
        timeout=dict(type='int', default=30),
        token_cache_path=dict(type='path', default='/tmp/.pki_token_cache'),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[
            ('action', 'ca_create', ['ca_cn', 'ca_org', 'ca_country']),
            ('action', 'ca_get', ['ca_id']),
            ('action', 'ca_revoke', ['ca_id']),
            ('action', 'ca_delete', ['ca_id']),
            ('action', 'cert_issue', ['ca_id', 'cert_cn']),
            ('action', 'cert_get', ['cert_id']),
            ('action', 'cert_renew', ['cert_id']),
            ('action', 'cert_revoke', ['cert_id']),
            ('action', 'cert_delete', ['cert_id']),
            ('action', 'cert_download', ['cert_id']),
            ('action', 'search', ['search_query']),
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
    )

    # Authenticate
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
                validity=module.params['ca_validity'],
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
            cert_type=module.params.get('cert_type') if module.params.get('cert_type') != 'server' else None,
        )

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

        if module.check_mode:
            result = {'changed': True, 'msg': 'Certificate would be downloaded (check mode)'}
        else:
            result = client.cert_download(
                cert_id=module.params['cert_id'],
                format=fmt,
                password=module.params.get('download_password'),
                dest=module.params.get('download_dest'),
            )

    # Return result
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
