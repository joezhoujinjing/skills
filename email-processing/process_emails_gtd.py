#!/usr/bin/env python3
"""
Process emails using GTD (Getting Things Done) principles.
Categorizes emails and suggests batch actions.
"""

import yaml
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def load_emails(yaml_file):
    """Load emails from YAML file."""
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    return data.get('emails', [])


def categorize_email(email):
    """Categorize email based on sender and content."""
    from_addr = email['metadata']['from'].lower()
    subject = email['metadata']['subject'].lower()

    # Extract domain
    if '<' in from_addr and '>' in from_addr:
        email_part = from_addr.split('<')[1].split('>')[0]
    else:
        email_part = from_addr.split()[-1] if ' ' in from_addr else from_addr

    domain = email_part.split('@')[-1] if '@' in email_part else 'unknown'

    # Categorize
    categories = []

    # Social/networking
    if 'linkedin.com' in domain:
        categories.append('social')
        if 'message' in subject:
            categories.append('direct_message')
        else:
            categories.append('notification')

    # Newsletters/content
    if any(d in domain for d in ['substack.com', 'medium.com', 'beehiiv.com', 'convertkit.com']):
        categories.append('newsletter')

    # Financial
    if any(d in domain for d in ['stripe.com', 'mercury.com', 'bill.com', 'expensify.com']):
        categories.append('financial')
        if any(w in subject for w in ['invoice', 'receipt', 'payment', 'charge']):
            categories.append('receipt')

    # Tools/SaaS
    if any(d in domain for d in ['anthropic.com', 'claude.com', 'openai.com', 'supabase.com',
                                   'vercel.com', 'rippling.com', 'vanta.com', 'fireflies.ai']):
        categories.append('saas_tool')

    # Project management
    if any(d in domain for d in ['trello.com', 'asana.com', 'notion.so']):
        categories.append('project_mgmt')

    # Company internal
    if 'multifi.ai' in domain:
        categories.append('internal')

    # Calendar
    if 'calendar' in subject or 'invitation' in subject or 'invite' in subject:
        categories.append('calendar')

    # Action required
    if any(w in subject for w in ['action required', 'urgent', 'approve', 'review', 'confirm']):
        categories.append('action_required')

    # Default to updates if no category
    if not categories:
        categories.append('update')

    return {
        'domain': domain,
        'categories': categories
    }


def analyze_emails(emails):
    """Analyze and categorize all emails."""
    by_domain = defaultdict(list)
    by_category = defaultdict(list)

    for email in emails:
        cat_info = categorize_email(email)
        domain = cat_info['domain']

        by_domain[domain].append(email)
        for cat in cat_info['categories']:
            by_category[cat].append(email)

    return by_domain, by_category


def print_summary(by_domain, by_category):
    """Print processing summary and recommendations."""
    print("=" * 80)
    print("📧 EMAIL PROCESSING ANALYSIS (GTD Method)")
    print("=" * 80)
    print()

    print("📊 BY DOMAIN:")
    print("-" * 80)
    for domain, emails in sorted(by_domain.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
        print(f"   {len(emails):3d} emails - {domain}")
    print()

    print("🏷️  BY CATEGORY:")
    print("-" * 80)
    for cat, emails in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"   {len(emails):3d} emails - {cat}")
    print()

    print("=" * 80)
    print("💡 RECOMMENDED BATCH ACTIONS:")
    print("=" * 80)
    print()

    # Recommendations
    actions = []

    # Newsletters - Archive unless you read them
    if 'newsletter' in by_category and len(by_category['newsletter']) > 5:
        actions.append({
            'priority': 1,
            'action': 'Archive newsletters (unless actively reading)',
            'count': len(by_category['newsletter']),
            'reason': 'Newsletters rarely require action - read or delete'
        })

    # Social notifications - Archive most
    if 'notification' in by_category and len(by_category['notification']) > 5:
        actions.append({
            'priority': 2,
            'action': 'Archive social notifications (LinkedIn, etc.)',
            'count': len(by_category['notification']),
            'reason': 'Social notifications are rarely urgent'
        })

    # Receipts - Archive after review
    if 'receipt' in by_category:
        actions.append({
            'priority': 3,
            'action': 'Quick scan receipts, then archive',
            'count': len(by_category['receipt']),
            'reason': 'Financial records - scan for errors then archive'
        })

    # Action required - Process immediately
    if 'action_required' in by_category:
        actions.append({
            'priority': 0,
            'action': '🚨 URGENT: Review action-required emails',
            'count': len(by_category['action_required']),
            'reason': 'These need your attention ASAP'
        })

    # Direct messages - Review and respond
    if 'direct_message' in by_category:
        actions.append({
            'priority': 1,
            'action': 'Review direct messages and respond',
            'count': len(by_category['direct_message']),
            'reason': 'Personal communication from contacts'
        })

    # Calendar invites - Accept/decline
    if 'calendar' in by_category:
        actions.append({
            'priority': 2,
            'action': 'Process calendar invitations',
            'count': len(by_category['calendar']),
            'reason': 'Accept or decline to clear inbox'
        })

    # Sort by priority
    actions.sort(key=lambda x: x['priority'])

    for i, action in enumerate(actions, 1):
        icon = "🔴" if action['priority'] == 0 else "🟡" if action['priority'] == 1 else "🟢"
        print(f"{icon} {i}. {action['action']}")
        print(f"   Count: {action['count']} emails")
        print(f"   Why: {action['reason']}")
        print()

    print("=" * 80)
    print("🎯 NEXT STEPS:")
    print("=" * 80)
    print()
    print("1. Open Gmail and work through the priority actions above")
    print("2. Use the 2-minute rule: if it takes <2min, do it now")
    print("3. For longer tasks: extract to your task system, then archive email")
    print("4. Batch similar emails together (all newsletters, all social, etc.)")
    print("5. Goal: Get inbox to zero by end of session")
    print()


def main():
    # Find most recent export file
    triage_dir = Path.home() / "email_triage"
    yaml_files = sorted(triage_dir.glob("unread_emails_*.yaml"), reverse=True)

    if not yaml_files:
        print("❌ No email export files found in ~/email_triage")
        print("   Run: python3 export_unprocessed.py first")
        sys.exit(1)

    yaml_file = yaml_files[0]
    print(f"📂 Loading emails from: {yaml_file.name}")
    print()

    emails = load_emails(yaml_file)
    by_domain, by_category = analyze_emails(emails)
    print_summary(by_domain, by_category)


if __name__ == "__main__":
    main()
