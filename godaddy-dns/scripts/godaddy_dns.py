#!/usr/bin/env python3
"""
GoDaddy DNS Management Script
Manage DNS records for GoDaddy-hosted domains via API v1.
"""

import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class GoDaddyDNS:
    """GoDaddy DNS API v1 client."""
    
    BASE_URL = "https://api.godaddy.com/v1"
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key or os.environ.get("GODADDY_API_KEY")
        self.api_secret = api_secret or os.environ.get("GODADDY_API_SECRET")
        
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "API credentials required. Set GODADDY_API_KEY and GODADDY_API_SECRET "
                "environment variables or pass them directly."
            )
    
    def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make an API request."""
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"sso-key {self.api_key}:{self.api_secret}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        body = json.dumps(data).encode() if data else None
        req = Request(url, data=body, headers=headers, method=method)
        
        try:
            with urlopen(req) as response:
                if response.status == 204:  # No content
                    return {"success": True}
                body = response.read().decode()
                if not body:  # Empty body
                    return {"success": True}
                return json.loads(body)
        except HTTPError as e:
            error_body = e.read().decode()
            try:
                error = json.loads(error_body)
                raise Exception(f"API Error ({e.code}): {error.get('message', error_body)}")
            except json.JSONDecodeError:
                raise Exception(f"API Error ({e.code}): {error_body}")
        except URLError as e:
            raise Exception(f"Network Error: {e.reason}")
    
    def list_domains(self, status: str = None) -> list:
        """List all domains in the account."""
        endpoint = "/domains"
        if status:
            endpoint += f"?statuses={status}"
        return self._request("GET", endpoint)
    
    def get_domain(self, domain: str) -> dict:
        """Get details for a specific domain."""
        return self._request("GET", f"/domains/{domain}")
    
    def list_records(self, domain: str, record_type: str = None, name: str = None) -> list:
        """List DNS records for a domain."""
        if record_type and name:
            endpoint = f"/domains/{domain}/records/{record_type}/{name}"
        elif record_type:
            endpoint = f"/domains/{domain}/records/{record_type}"
        else:
            endpoint = f"/domains/{domain}/records"
        return self._request("GET", endpoint)
    
    def add_record(self, domain: str, record_type: str, name: str, data: str,
                   ttl: int = 3600, priority: int = None) -> dict:
        """Add a new DNS record."""
        record = {
            "type": record_type,
            "name": name,
            "data": data,
            "ttl": ttl,
        }
        if priority is not None:
            record["priority"] = priority
        
        return self._request("PATCH", f"/domains/{domain}/records", [record])
    
    def update_record(self, domain: str, record_type: str, name: str, data: str,
                      ttl: int = 3600, priority: int = None) -> dict:
        """Update/replace a DNS record by type and name."""
        record = {
            "data": data,
            "ttl": ttl,
        }
        if priority is not None:
            record["priority"] = priority
        
        return self._request("PUT", f"/domains/{domain}/records/{record_type}/{name}", [record])
    
    def delete_record(self, domain: str, record_type: str, name: str) -> dict:
        """Delete a DNS record by type and name."""
        return self._request("DELETE", f"/domains/{domain}/records/{record_type}/{name}")
    
    def replace_all_records(self, domain: str, records: list) -> dict:
        """Replace all DNS records for a domain."""
        return self._request("PUT", f"/domains/{domain}/records", records)


def format_table(records: list, columns: list = None) -> str:
    """Format records as a table."""
    if not records:
        return "No records found."
    
    if columns is None:
        columns = ["type", "name", "data", "ttl"]
    
    # Add priority column if any record has it
    if any("priority" in r for r in records):
        columns = ["type", "name", "data", "ttl", "priority"]
    
    # Calculate column widths
    widths = {col: len(col) for col in columns}
    for record in records:
        for col in columns:
            val = str(record.get(col, ""))
            widths[col] = max(widths[col], len(val))
    
    # Build table
    header = " | ".join(col.upper().ljust(widths[col]) for col in columns)
    separator = "-+-".join("-" * widths[col] for col in columns)
    rows = []
    for record in records:
        row = " | ".join(str(record.get(col, "")).ljust(widths[col]) for col in columns)
        rows.append(row)
    
    return "\n".join([header, separator] + rows)


def format_domains(domains: list) -> str:
    """Format domains as a table."""
    if not domains:
        return "No domains found."
    
    columns = ["domain", "status", "expires"]
    widths = {col: len(col) for col in columns}
    
    for domain in domains:
        widths["domain"] = max(widths["domain"], len(domain.get("domain", "")))
        widths["status"] = max(widths["status"], len(domain.get("status", "")))
        expires = domain.get("expires", "")[:10] if domain.get("expires") else ""
        widths["expires"] = max(widths["expires"], len(expires))
    
    header = " | ".join(col.upper().ljust(widths[col]) for col in columns)
    separator = "-+-".join("-" * widths[col] for col in columns)
    rows = []
    for domain in domains:
        expires = domain.get("expires", "")[:10] if domain.get("expires") else ""
        row = " | ".join([
            domain.get("domain", "").ljust(widths["domain"]),
            domain.get("status", "").ljust(widths["status"]),
            expires.ljust(widths["expires"]),
        ])
        rows.append(row)
    
    return "\n".join([header, separator] + rows)


def main():
    parser = argparse.ArgumentParser(
        description="GoDaddy DNS Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--key", help="GoDaddy API key")
    parser.add_argument("--secret", help="GoDaddy API secret")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list-domains
    p_domains = subparsers.add_parser("list-domains", help="List all domains")
    p_domains.add_argument("--status", help="Filter by status (e.g., ACTIVE)")
    p_domains.add_argument("--json", action="store_true", help="Output as JSON")
    
    # list-records
    p_records = subparsers.add_parser("list-records", help="List DNS records")
    p_records.add_argument("domain", help="Domain name")
    p_records.add_argument("--type", dest="record_type", help="Filter by record type")
    p_records.add_argument("--name", help="Filter by record name")
    p_records.add_argument("--json", action="store_true", help="Output as JSON")
    
    # add-record
    p_add = subparsers.add_parser("add-record", help="Add a DNS record")
    p_add.add_argument("domain", help="Domain name")
    p_add.add_argument("type", help="Record type (A, AAAA, CNAME, MX, TXT, NS, SRV, CAA)")
    p_add.add_argument("name", help="Record name (@ for root)")
    p_add.add_argument("data", help="Record data")
    p_add.add_argument("--ttl", type=int, default=3600, help="TTL in seconds (default: 3600)")
    p_add.add_argument("--priority", type=int, help="Priority (for MX, SRV)")
    
    # update-record
    p_update = subparsers.add_parser("update-record", help="Update a DNS record")
    p_update.add_argument("domain", help="Domain name")
    p_update.add_argument("type", help="Record type")
    p_update.add_argument("name", help="Record name (@ for root)")
    p_update.add_argument("data", help="New record data")
    p_update.add_argument("--ttl", type=int, default=3600, help="TTL in seconds (default: 3600)")
    p_update.add_argument("--priority", type=int, help="Priority (for MX, SRV)")
    
    # delete-record
    p_delete = subparsers.add_parser("delete-record", help="Delete a DNS record")
    p_delete.add_argument("domain", help="Domain name")
    p_delete.add_argument("type", help="Record type")
    p_delete.add_argument("name", help="Record name (@ for root)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        client = GoDaddyDNS(api_key=args.key, api_secret=args.secret)
        
        if args.command == "list-domains":
            result = client.list_domains(status=args.status)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(format_domains(result))
        
        elif args.command == "list-records":
            result = client.list_records(
                args.domain,
                record_type=args.record_type,
                name=args.name
            )
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(format_table(result))
        
        elif args.command == "add-record":
            result = client.add_record(
                args.domain,
                args.type.upper(),
                args.name,
                args.data,
                ttl=args.ttl,
                priority=args.priority
            )
            print(f"✓ Added {args.type.upper()} record for {args.name}.{args.domain}")
        
        elif args.command == "update-record":
            result = client.update_record(
                args.domain,
                args.type.upper(),
                args.name,
                args.data,
                ttl=args.ttl,
                priority=args.priority
            )
            print(f"✓ Updated {args.type.upper()} record for {args.name}.{args.domain}")
        
        elif args.command == "delete-record":
            result = client.delete_record(args.domain, args.type.upper(), args.name)
            print(f"✓ Deleted {args.type.upper()} record for {args.name}.{args.domain}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
