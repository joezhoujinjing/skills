import yaml
import sys
from pathlib import Path

# Category definitions
CATEGORIES = {
    'calendar': ['calendar', 'invitation', 'invite', 'google.com'],
    'financial': ['stripe.com', 'mercury.com', 'bill.com', 'expensify.com', 'brex.com', 'ramp.com', 'receipt', 'invoice', 'payment', 'charge'],
    'direct_message': ['message', 'via linkedin', 'intro', 'hello', 'hi ', 'meeting', 'sync']
}

def is_category(email, category):
    sender = email['metadata']['from'].lower()
    subject = email['metadata']['subject'].lower()
    
    # Specific logic for each
    if category == 'calendar':
        if 'invitation' in subject or 'accepted' in subject or 'declined' in subject or 'updated' in subject or 'canceled' in subject:
            return True
        if 'google calendar' in sender:
            return True
            
    elif category == 'financial':
        if any(d in sender for d in ['stripe.com', 'mercury.com', 'bill.com', 'expensify.com', 'brex.com', 'ramp.com', 'quickbooks']):
            return True
        if any(w in subject for w in ['receipt', 'invoice', 'payment', 'transaction']):
            return True
            
    elif category == 'direct_message':
        # Harder to detect perfectly without more sophisticated logic, but let's try
        # Exclude notifications/newsletters
        if any(d in sender for d in ['no-reply', 'noreply', 'notification', 'newsletter', 'info@', 'support@', 'team@']):
            return False
        # If it looks like a person
        if 'via linkedin' in sender and 'message' in subject:
             return True
        # If it's not a known tool/notification
        return True

    return False

def main():
    triage_dir = Path.home() / "email_triage"
    # Re-use the file we just loaded (assuming the previous archive operation didn't update the YAML file on disk, 
    # but we should probably fetch fresh if we want to be 100% accurate. 
    # However, since we just archived 195 emails, the local YAML is stale. 
    # We should filter the local YAML against the list of IDs we know are archived?
    # Or just show what WAS in the list and let the user decide, then we re-check existence?
    # Better: Show from the existing YAML but filter out the ones we just archived?
    # Actually, we didn't save the archived IDs anywhere persistent.
    # Let's just use the existing YAML. The archiving happened on the server.
    # If I try to archive an already archived email, it's fine (idempotent).
    # But for display, we might show emails that are already gone.
    # Let's just list them.
    
    yaml_files = sorted(triage_dir.glob("unread_emails_*.yaml"), reverse=True)
    if not yaml_files:
        print("No file.")
        return
        
    with open(yaml_files[0]) as f:
        data = yaml.safe_load(f)

    # We need to filter out the ones we likely just archived (social/saas) to avoid confusion?
    # Or just show the specific categories requested.
    
    calendar_emails = []
    financial_emails = []
    dm_emails = []
    
    for email in data.get('emails', []):
        # Skip if it matches the social/saas patterns we just archived
        sender = email['metadata']['from'].lower()
        if any(x in sender for x in ['vanta.com', 'fireflies.ai', 'slack.com', 'claude.com', 'anthropic.com', 'linkedin.com', 'substack.com', 'medium.com']):
            # These are likely archived, skip them to reduce noise
            continue

        if is_category(email, 'calendar'):
            calendar_emails.append(email)
        elif is_category(email, 'financial'):
            financial_emails.append(email)
        elif is_category(email, 'direct_message'):
            dm_emails.append(email)

    print(f"\n📅 CALENDAR INVITES ({len(calendar_emails)}):")
    for e in calendar_emails:
        print(f"  - {e['metadata']['subject']} (From: {e['metadata']['from']})")

    print(f"\n💰 FINANCIAL / RECEIPTS ({len(financial_emails)}):")
    for e in financial_emails:
        print(f"  - {e['metadata']['subject']} (From: {e['metadata']['from']})")

    print(f"\n💬 DIRECT MESSAGES ({len(dm_emails)}):")
    for e in dm_emails:
        print(f"  - {e['metadata']['subject']} (From: {e['metadata']['from']})")

if __name__ == "__main__":
    main()
