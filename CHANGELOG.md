# Changelog

All notable changes to the `oriolrius.pki_manager` collection. Versions follow
semantic versioning. Each version has a GitHub release with the full notes.

## Unreleased

### Changed

- Integration tests run PKI Manager 4 with OpenBao (the PKI Manager fork) and no Cosmian KMS. The OpenBao config, policies, bootstrap and pinned image come from the `openbao/` folder of the PKI Manager release under test. The backend gets a scoped token, and the run checks its scope and that the keys are in OpenBao Transit. PKI Manager 3.x (Cosmian) is no longer in the test matrix. The module and the roles do not change.

## 3.1.0 (2026-11-26)

### Added

- Actions for CRLs (`crl_list`, `crl_generate`, `crl_download`), the CA download (`ca_download`), CA certificates (`ca_certs`), bulk (`cert_bulk_renew`, `cert_bulk_revoke`, `cert_bulk_delete`), `domain_list`, `audit_list`, `report_generate`, and the SSH lifecycle (CA get/rotate/retire/revoke, KRL, host get/issue/revoke/offboard, identity disable/offboard, principal revoke-grant/unmap/delete, token revoke, certificate revoke, metrics, trust anchors, SSH bulk, zone archive/unarchive) (#8).
- `api_request`: any REST operation, or a public root route, with the module's authentication, retry and errors (#8).
- Options of the 3.19 API: `renew_new_key`, `revoke_original` and subject/SAN changes for `cert_renew`; `revocation_effective_date`, `generate_crl`; `destroy_key`, `remove_from_crl`; `tags`; `user_extensions`, `force_command`, `source_address`, `user_key_id`; `allowed_principals`, `max_valid_seconds` (#7).
- HTTP 429 retry: `rate_limit_retries` and `rate_limit_max_wait` (#9).
- CI: ansible-lint, yamllint, `ansible-test sanity`, and integration tests against a real PKI Manager with both roles run twice (the second run must change nothing) (#10).

### Fixed

- `pki_host_setup`: a PKCS#12 entry failed in 3.0.1 (the fullchain lookup ran for it).
- Both roles work on a minimal host with no `ip` command (no IPv4 facts).

## 3.0.1 (2026-11-26)

### Security

- `pki_host_setup` no longer writes the private key to `<name>-fullchain.crt` (mode 0644). A host with such a file gets a new certificate, and the old one is revoked with reason `keyCompromise` (GHSA-fvgg-75hc-jv7g).

### Added

- `cert_find`, `revocation_details`; `cert_download` is idempotent with `download_dest`.

## 3.0.0 (2026-11-26)

Fixes from a review against PKI Manager 3.19.0, and SSH zones. Breaking: RSA-only `ca_algorithm`, two revocation reasons removed, `cert_org`/`cert_country` required for `cert_issue`, token cache location, `cert_type` has no default for `cert_list`.

- `ca_validity_years` (the API takes years; `ca_validity` in days was ignored), the export password in a header, a per-server token cache, `auth_test` on an authenticated endpoint, Fastify error messages, every page of `ca_list`/`cert_list`, `api_token`, `ca_path`.
- `pki_host_setup`: idempotent (state file per certificate), API calls on the controller, default SANs with two labels or more, the replaced certificate is revoked.
- SSH zones: `zone` option, `ssh_zone_list`, `ssh_zone_create`, `ssh_host_cert_zone`.

## 2.5.0

- `ssh_host_cert`: acknowledge principal pushes (`ssh_principals_pushed`).

## 2.4.0

- `ssh_host_cert`: always generate an `ecdsa-sha2-nistp256` host key.

## 2.3.1

- README rebuild.

## 2.3.0

- SSH certificate workflow: SSH actions and the `ssh_host_cert` role.

## 2.2.0

- `dual` certificate type (mTLS).

## 2.1.0 – 2.1.3

- `pki_host_setup` role, field and subject fixes, packaged examples, docs.

## 2.0.0 – 2.0.1

- The module as an Ansible collection; Galaxy compatibility fix.

## 1.0.0

- First release: the `pki_manager` module.
