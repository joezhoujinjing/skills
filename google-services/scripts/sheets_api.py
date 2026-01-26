#!/usr/bin/env python3
"""
Google Sheets API helper for Google Services skill.
"""

import argparse
import sys
import json
from googleapiclient.discovery import build
from oauth_helper import get_credentials, print_auth_info


def create_spreadsheet(service, title, sheet_name=None):
    """Create a new Google Sheet."""
    try:
        spreadsheet = {"properties": {"title": title}}
        if sheet_name:
            spreadsheet["sheets"] = [{"properties": {"title": sheet_name}}]

        result = service.spreadsheets().create(body=spreadsheet).execute()

        spreadsheet_id = result["spreadsheetId"]
        print(f"✅ Spreadsheet created successfully!")
        print(f"   Title: {result['properties']['title']}")
        print(f"   ID: {spreadsheet_id}")
        print(f"   Link: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")

        return spreadsheet_id

    except Exception as e:
        print(f"❌ Error creating spreadsheet: {e}", file=sys.stderr)
        sys.exit(1)


def read_range(service, spreadsheet_id, range_name):
    """Read data from a sheet range."""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()

        values = result.get("values", [])

        if not values:
            print("No data found in range.")
            return

        print(f"\n{'=' * 100}")
        print(f"Spreadsheet ID: {spreadsheet_id}")
        print(f"Range: {range_name}")
        print(f"Link: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
        print(f"{'=' * 100}\n")

        # Print data as table
        for row in values:
            print("  ".join([str(cell).ljust(20) for cell in row]))

        print(f"\n{'=' * 100}")
        print(f"Found {len(values)} rows")

    except Exception as e:
        print(f"❌ Error reading range: {e}", file=sys.stderr)
        sys.exit(1)


def update_range(service, spreadsheet_id, range_name, values):
    """Update data in a sheet range."""
    try:
        # Parse values from JSON string
        if isinstance(values, str):
            values = json.loads(values)

        body = {"values": values}

        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

        print(f"✅ Range updated successfully!")
        print(f"   Updated cells: {result.get('updatedCells')}")
        print(f"   Updated range: {result.get('updatedRange')}")
        print(f"   Link: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")

    except Exception as e:
        print(f"❌ Error updating range: {e}", file=sys.stderr)
        sys.exit(1)


def append_rows(service, spreadsheet_id, range_name, values):
    """Append rows to a sheet."""
    try:
        # Parse values from JSON string
        if isinstance(values, str):
            values = json.loads(values)

        body = {"values": values}

        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

        print(f"✅ Rows appended successfully!")
        print(f"   Updated cells: {result.get('updates', {}).get('updatedCells')}")
        print(f"   Updated range: {result.get('updates', {}).get('updatedRange')}")
        print(f"   Link: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")

    except Exception as e:
        print(f"❌ Error appending rows: {e}", file=sys.stderr)
        sys.exit(1)


def get_spreadsheet_info(service, spreadsheet_id):
    """Get spreadsheet metadata."""
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

        print(f"\n{'=' * 100}")
        print(f"Title: {spreadsheet['properties']['title']}")
        print(f"ID: {spreadsheet_id}")
        print(f"Link: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
        print(f"{'=' * 100}\n")

        sheets = spreadsheet.get("sheets", [])
        print(f"Sheets ({len(sheets)}):")
        for sheet in sheets:
            props = sheet["properties"]
            print(f"  📊 {props['title']}")
            print(f"     Sheet ID: {props['sheetId']}")
            print(f"     Rows: {props['gridProperties']['rowCount']}")
            print(f"     Columns: {props['gridProperties']['columnCount']}")

        print(f"\n{'=' * 100}")

    except Exception as e:
        print(f"❌ Error getting spreadsheet info: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Google Sheets API Helper")
    parser.add_argument("command", choices=["create", "read", "update", "append", "info"],
                        help="Command to execute")
    parser.add_argument("--title", help="Spreadsheet title")
    parser.add_argument("--sheet-name", help="Sheet name")
    parser.add_argument("--spreadsheet-id", help="Spreadsheet ID")
    parser.add_argument("--range", help="Range in A1 notation (e.g., Sheet1!A1:B10)")
    parser.add_argument("--values", help="Values as JSON array (e.g., '[[\"A\",\"B\"],[\"1\",\"2\"]]')")
    parser.add_argument("--refresh-token-secret", help="Secret name for refresh token")

    args = parser.parse_args()

    # Get credentials
    print_auth_info("Sheets")
    credentials = get_credentials(refresh_token_secret=args.refresh_token_secret)

    # Build Sheets service
    service = build("sheets", "v4", credentials=credentials)

    # Execute command
    if args.command == "create":
        if not args.title:
            print("❌ --title is required for create command", file=sys.stderr)
            sys.exit(1)
        create_spreadsheet(service, args.title, sheet_name=args.sheet_name)
    elif args.command == "read":
        if not args.spreadsheet_id or not args.range:
            print("❌ --spreadsheet-id and --range are required for read command", file=sys.stderr)
            sys.exit(1)
        read_range(service, args.spreadsheet_id, args.range)
    elif args.command == "update":
        if not all([args.spreadsheet_id, args.range, args.values]):
            print("❌ --spreadsheet-id, --range, and --values are required for update command", file=sys.stderr)
            sys.exit(1)
        update_range(service, args.spreadsheet_id, args.range, args.values)
    elif args.command == "append":
        if not all([args.spreadsheet_id, args.range, args.values]):
            print("❌ --spreadsheet-id, --range, and --values are required for append command", file=sys.stderr)
            sys.exit(1)
        append_rows(service, args.spreadsheet_id, args.range, args.values)
    elif args.command == "info":
        if not args.spreadsheet_id:
            print("❌ --spreadsheet-id is required for info command", file=sys.stderr)
            sys.exit(1)
        get_spreadsheet_info(service, args.spreadsheet_id)


if __name__ == "__main__":
    main()
