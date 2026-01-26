#!/usr/bin/env python3
"""
Google Calendar API helper for Google Services skill.
"""

import argparse
import sys
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from oauth_helper import get_credentials, print_auth_info


def list_calendars(service):
    """List all calendars."""
    try:
        calendars = service.calendarList().list().execute()

        if not calendars.get("items"):
            print("No calendars found.")
            return

        print(f"Found {len(calendars['items'])} calendars:\n")
        print("=" * 100)

        for calendar in calendars["items"]:
            print(f"\n📅 {calendar['summary']}")
            print(f"   ID: {calendar['id']}")
            print(f"   Primary: {calendar.get('primary', False)}")
            print(f"   Access Role: {calendar.get('accessRole', 'N/A')}")
            print("-" * 100)

    except Exception as e:
        print(f"❌ Error listing calendars: {e}", file=sys.stderr)
        sys.exit(1)


def list_events(service, calendar_id="primary", max_results=10, time_min=None, time_max=None):
    """List calendar events."""
    try:
        # Default to next 7 days if no time range specified
        if not time_min:
            time_min = datetime.utcnow().isoformat() + "Z"
        if not time_max:
            time_max = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"

        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        print(f"Found {len(events)} upcoming events:\n")
        print("=" * 100)

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))
            summary = event.get("summary", "No Title")
            description = event.get("description", "")
            location = event.get("location", "")

            print(f"\n📆 {summary}")
            print(f"   ID: {event['id']}")
            print(f"   Start: {start}")
            print(f"   End: {end}")
            if location:
                print(f"   Location: {location}")
            if description:
                print(f"   Description: {description[:100]}{'...' if len(description) > 100 else ''}")
            print(f"   Link: {event.get('htmlLink', 'N/A')}")
            print("-" * 100)

    except Exception as e:
        print(f"❌ Error listing events: {e}", file=sys.stderr)
        sys.exit(1)


def create_event(service, summary, start, end, calendar_id="primary", description=None, location=None, attendees=None):
    """Create a calendar event."""
    try:
        # Parse datetime strings
        if "T" not in start:
            start_time = {"date": start}
        else:
            start_time = {"dateTime": start, "timeZone": "UTC"}

        if "T" not in end:
            end_time = {"date": end}
        else:
            end_time = {"dateTime": end, "timeZone": "UTC"}

        event = {
            "summary": summary,
            "start": start_time,
            "end": end_time,
        }

        if description:
            event["description"] = description
        if location:
            event["location"] = location
        if attendees:
            event["attendees"] = [{"email": email.strip()} for email in attendees.split(",")]

        result = service.events().insert(calendarId=calendar_id, body=event).execute()

        print(f"✅ Event created successfully!")
        print(f"   Title: {result['summary']}")
        print(f"   ID: {result['id']}")
        print(f"   Start: {result['start']}")
        print(f"   End: {result['end']}")
        print(f"   Link: {result.get('htmlLink', 'N/A')}")

    except Exception as e:
        print(f"❌ Error creating event: {e}", file=sys.stderr)
        sys.exit(1)


def update_event(service, event_id, calendar_id="primary", summary=None, start=None, end=None, description=None, location=None):
    """Update a calendar event."""
    try:
        # Get existing event
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

        # Update fields
        if summary:
            event["summary"] = summary
        if start:
            event["start"] = {"dateTime": start, "timeZone": "UTC"} if "T" in start else {"date": start}
        if end:
            event["end"] = {"dateTime": end, "timeZone": "UTC"} if "T" in end else {"date": end}
        if description:
            event["description"] = description
        if location:
            event["location"] = location

        result = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()

        print(f"✅ Event updated successfully!")
        print(f"   Title: {result['summary']}")
        print(f"   Link: {result.get('htmlLink', 'N/A')}")

    except Exception as e:
        print(f"❌ Error updating event: {e}", file=sys.stderr)
        sys.exit(1)


def delete_event(service, event_id, calendar_id="primary"):
    """Delete a calendar event."""
    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        print(f"✅ Event deleted successfully!")
        print(f"   Event ID: {event_id}")

    except Exception as e:
        print(f"❌ Error deleting event: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Google Calendar API Helper")
    parser.add_argument("command", choices=["list-calendars", "list-events", "create-event", "update-event", "delete-event"],
                        help="Command to execute")
    parser.add_argument("--calendar-id", default="primary", help="Calendar ID")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum results")
    parser.add_argument("--event-id", help="Event ID for update/delete")
    parser.add_argument("--summary", help="Event title")
    parser.add_argument("--start", help="Start time (ISO 8601 format)")
    parser.add_argument("--end", help="End time (ISO 8601 format)")
    parser.add_argument("--description", help="Event description")
    parser.add_argument("--location", help="Event location")
    parser.add_argument("--attendees", help="Comma-separated list of attendee emails")
    parser.add_argument("--time-min", help="Minimum time for event search")
    parser.add_argument("--time-max", help="Maximum time for event search")
    parser.add_argument("--refresh-token-secret", help="Secret name for refresh token")

    args = parser.parse_args()

    # Get credentials
    print_auth_info("Calendar")
    credentials = get_credentials(refresh_token_secret=args.refresh_token_secret)

    # Build Calendar service
    service = build("calendar", "v3", credentials=credentials)

    # Execute command
    if args.command == "list-calendars":
        list_calendars(service)
    elif args.command == "list-events":
        list_events(service, calendar_id=args.calendar_id, max_results=args.max_results,
                    time_min=args.time_min, time_max=args.time_max)
    elif args.command == "create-event":
        if not all([args.summary, args.start, args.end]):
            print("❌ --summary, --start, and --end are required for create-event", file=sys.stderr)
            sys.exit(1)
        create_event(service, args.summary, args.start, args.end,
                     calendar_id=args.calendar_id, description=args.description,
                     location=args.location, attendees=args.attendees)
    elif args.command == "update-event":
        if not args.event_id:
            print("❌ --event-id is required for update-event", file=sys.stderr)
            sys.exit(1)
        update_event(service, args.event_id, calendar_id=args.calendar_id,
                     summary=args.summary, start=args.start, end=args.end,
                     description=args.description, location=args.location)
    elif args.command == "delete-event":
        if not args.event_id:
            print("❌ --event-id is required for delete-event", file=sys.stderr)
            sys.exit(1)
        delete_event(service, args.event_id, calendar_id=args.calendar_id)


if __name__ == "__main__":
    main()
