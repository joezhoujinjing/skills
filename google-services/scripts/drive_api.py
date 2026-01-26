#!/usr/bin/env python3
"""
Google Drive API helper for Google Services skill.
"""

import argparse
import sys
import io
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from oauth_helper import get_credentials, print_auth_info


def list_files(service, folder_id=None, max_results=20):
    """List files in Google Drive."""
    try:
        query = None
        if folder_id:
            query = f"'{folder_id}' in parents and trashed=false"
        else:
            query = "trashed=false"

        results = service.files().list(
            q=query,
            pageSize=max_results,
            fields="files(id, name, mimeType, modifiedTime, size, webViewLink)",
            orderBy="modifiedTime desc"
        ).execute()

        files = results.get("files", [])

        if not files:
            print("No files found.")
            return

        print(f"Found {len(files)} files:\n")
        print("=" * 120)

        for file in files:
            file_type = "📁" if file["mimeType"] == "application/vnd.google-apps.folder" else "📄"
            size = file.get("size", "N/A")
            if size != "N/A":
                size = f"{int(size) / 1024:.1f} KB" if int(size) < 1024 * 1024 else f"{int(size) / (1024 * 1024):.1f} MB"

            print(f"\n{file_type} {file['name']}")
            print(f"   ID: {file['id']}")
            print(f"   Type: {file['mimeType']}")
            print(f"   Modified: {file['modifiedTime']}")
            print(f"   Size: {size}")
            print(f"   Link: {file.get('webViewLink', 'N/A')}")
            print("-" * 120)

    except Exception as e:
        print(f"❌ Error listing files: {e}", file=sys.stderr)
        sys.exit(1)


def search_files(service, query, max_results=20):
    """Search files in Google Drive."""
    try:
        results = service.files().list(
            q=f"{query} and trashed=false",
            pageSize=max_results,
            fields="files(id, name, mimeType, modifiedTime, size, webViewLink)"
        ).execute()

        files = results.get("files", [])

        if not files:
            print(f"No files found matching query: {query}")
            return

        print(f"Found {len(files)} files matching '{query}':\n")
        print("=" * 120)

        for file in files:
            file_type = "📁" if file["mimeType"] == "application/vnd.google-apps.folder" else "📄"
            print(f"\n{file_type} {file['name']}")
            print(f"   ID: {file['id']}")
            print(f"   Type: {file['mimeType']}")
            print(f"   Link: {file.get('webViewLink', 'N/A')}")
            print("-" * 120)

    except Exception as e:
        print(f"❌ Error searching files: {e}", file=sys.stderr)
        sys.exit(1)


def download_file(service, file_id, output_path):
    """Download a file from Google Drive."""
    try:
        # Get file metadata
        file_metadata = service.files().get(fileId=file_id, fields="name,mimeType").execute()
        file_name = file_metadata["name"]
        mime_type = file_metadata["mimeType"]

        print(f"📥 Downloading: {file_name}")
        print(f"   Type: {mime_type}")

        # Handle Google Workspace files (export as PDF or other format)
        if mime_type.startswith("application/vnd.google-apps"):
            export_formats = {
                "application/vnd.google-apps.document": "application/pdf",
                "application/vnd.google-apps.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.google-apps.presentation": "application/pdf",
            }
            export_mime = export_formats.get(mime_type, "application/pdf")
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)

            if not output_path.endswith((".pdf", ".xlsx")):
                ext = ".pdf" if export_mime == "application/pdf" else ".xlsx"
                output_path = output_path + ext
        else:
            request = service.files().get_media(fileId=file_id)

        # Download
        fh = io.FileIO(output_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"   Progress: {int(status.progress() * 100)}%")

        print(f"✅ Downloaded to: {output_path}")

    except Exception as e:
        print(f"❌ Error downloading file: {e}", file=sys.stderr)
        sys.exit(1)


def upload_file(service, file_path, folder_id=None, name=None):
    """Upload a file to Google Drive."""
    try:
        file_name = name if name else os.path.basename(file_path)

        file_metadata = {"name": file_name}
        if folder_id:
            file_metadata["parents"] = [folder_id]

        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, name, webViewLink"
        ).execute()

        print(f"✅ File uploaded successfully!")
        print(f"   Name: {file['name']}")
        print(f"   ID: {file['id']}")
        print(f"   Link: {file.get('webViewLink', 'N/A')}")

    except Exception as e:
        print(f"❌ Error uploading file: {e}", file=sys.stderr)
        sys.exit(1)


def create_folder(service, name, parent_folder_id=None):
    """Create a folder in Google Drive."""
    try:
        file_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        if parent_folder_id:
            file_metadata["parents"] = [parent_folder_id]

        folder = service.files().create(body=file_metadata, fields="id, name, webViewLink").execute()

        print(f"✅ Folder created successfully!")
        print(f"   Name: {folder['name']}")
        print(f"   ID: {folder['id']}")
        print(f"   Link: {folder.get('webViewLink', 'N/A')}")

    except Exception as e:
        print(f"❌ Error creating folder: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Google Drive API Helper")
    parser.add_argument("command", choices=["list", "search", "download", "upload", "create-folder"],
                        help="Command to execute")
    parser.add_argument("--folder-id", help="Folder ID for list/upload")
    parser.add_argument("--max-results", type=int, default=20, help="Maximum results")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--file-id", help="File ID for download")
    parser.add_argument("--output", help="Output path for download")
    parser.add_argument("--file-path", help="File path for upload")
    parser.add_argument("--name", help="Name for upload/create-folder")
    parser.add_argument("--refresh-token-secret", help="Secret name for refresh token")

    args = parser.parse_args()

    # Get credentials
    print_auth_info("Drive")
    credentials = get_credentials(refresh_token_secret=args.refresh_token_secret)

    # Build Drive service
    service = build("drive", "v3", credentials=credentials)

    # Execute command
    if args.command == "list":
        list_files(service, folder_id=args.folder_id, max_results=args.max_results)
    elif args.command == "search":
        if not args.query:
            print("❌ --query is required for search command", file=sys.stderr)
            sys.exit(1)
        search_files(service, args.query, max_results=args.max_results)
    elif args.command == "download":
        if not args.file_id or not args.output:
            print("❌ --file-id and --output are required for download command", file=sys.stderr)
            sys.exit(1)
        download_file(service, args.file_id, args.output)
    elif args.command == "upload":
        if not args.file_path:
            print("❌ --file-path is required for upload command", file=sys.stderr)
            sys.exit(1)
        upload_file(service, args.file_path, folder_id=args.folder_id, name=args.name)
    elif args.command == "create-folder":
        if not args.name:
            print("❌ --name is required for create-folder command", file=sys.stderr)
            sys.exit(1)
        create_folder(service, args.name, parent_folder_id=args.folder_id)


if __name__ == "__main__":
    main()
