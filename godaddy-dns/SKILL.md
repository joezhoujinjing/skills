---
name: godaddy-dns
description: GoDaddy DNS management skill for managing domain DNS records via GoDaddy API v1. Use when the user wants to list domains, view DNS records, add/create DNS records, update/edit DNS records, or delete DNS records for domains hosted on GoDaddy. Supports A, AAAA, CNAME, MX, TXT, NS, SRV, and CAA record types.
---

# GoDaddy DNS Management

Manage DNS records for GoDaddy-hosted domains using the GoDaddy API v1.

## Configuration

Get API credentials from secret-vault skill:

- `/secret-vault get shared-godaddy-dns-api-key`
- `/secret-vault get shared-godaddy-dns-api-secret`

Set as environment variables: `GODADDY_API_KEY` and `GODADDY_API_SECRET`

Get credentials at: https://developer.godaddy.com/keys

## Commands

```bash
# List domains
python3 scripts/godaddy_dns.py list-domains

# List records (optional: --type TYPE --name NAME)
python3 scripts/godaddy_dns.py list-records example.com

# Add record (MX requires --priority)
python3 scripts/godaddy_dns.py add-record example.com TYPE NAME DATA [--ttl TTL] [--priority PRIORITY]

# Update record
python3 scripts/godaddy_dns.py update-record example.com TYPE NAME DATA [--ttl TTL]

# Delete record
python3 scripts/godaddy_dns.py delete-record example.com TYPE NAME
```

## Examples

```bash
# A record
python3 scripts/godaddy_dns.py add-record example.com A www 192.168.1.1
python3 scripts/godaddy_dns.py update-record example.com A @ 1.2.3.4

# CNAME
python3 scripts/godaddy_dns.py add-record example.com CNAME www example.com

# MX (email)
python3 scripts/godaddy_dns.py add-record example.com MX @ mail.example.com --priority 10

# TXT (SPF, verification, etc.)
python3 scripts/godaddy_dns.py add-record example.com TXT @ "v=spf1 include:_spf.google.com ~all"
```

## Record Types

A, AAAA, CNAME, MX, TXT, NS, SRV, CAA

## Notes

- Default TTL: 3600s | `@` = root domain | Rate limit: 60/min | Propagation: minutes to 48h
- Full API docs: `references/api_reference.md`
