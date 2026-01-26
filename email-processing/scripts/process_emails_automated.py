#!/usr/bin/env python3
"""
Automated email processing based on predefined rules.
For remote/headless processing without interactive prompts.
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import json


def load_emails():
    """Load emails from the dump file."""
    skill_dir = Path(__file__).parent.parent
    dump_file = skill_dir / "data" / "emails_dump.yaml"

    if not dump_file.exists():
        print("❌ No data/emails_dump.yaml found!")
        print("   Run: python scripts/export_unprocessed.py first")
        sys.exit(1)

    with open(dump_file, 'r') as f:
        data = yaml.safe_load(f)

    return data.get('emails', [])


def load_processing_rules():
    """Load processing rules from config file."""
    skill_dir = Path(__file__).parent
    rules_file = skill_dir / "processing_rules.yaml"

    if not rules_file.exists():
        # Return default rules
        return {
            'auto_archive_categories': [
                'newsletter',
                'notification',
                'receipt',
                'calendar'
            ],
            'auto_archive_domains': [
                'linkedin.com',
                'substack.com',
                'medium.com',
                'beehiiv.com',
                'convertkit.com'
            ],
            'require_review_keywords': [
                'action required',
                'urgent',
                'approve',
                'approval needed',
                'deadline',
                'overdue'
            ],
            'auto_trello_keywords': [
                'review',
                'proposal',
                'contract',
                'agreement'
            ]
        }

    with open(rules_file, 'r') as f:
        return yaml.safe_load(f)


def categorize_email(email):
    """Categorize email and determine processing action."""
    subject = email['metadata']['subject'].lower()
    from_addr = email['metadata']['from'].lower()

    # Extract domain
    if '<' in from_addr and '>' in from_addr:
        email_part = from_addr.split('<')[1].split('>')[0]
    else:
        email_part = from_addr.split()[-1] if ' ' in from_addr else from_addr

    domain = email_part.split('@')[-1] if '@' in email_part else 'unknown'

    result = {
        'domain': domain,
        'category': 'other',
        'action': 'review',  # default: needs manual review
        'priority': 3,
        'reason': 'Default - needs review'
    }

    # Check for urgent/action required
    urgent_keywords = ['action required', 'urgent', 'approve', 'approval needed',
                      'deadline', 'overdue', 'confirm', 'verification']
    if any(kw in subject for kw in urgent_keywords):
        result['category'] = 'urgent'
        result['action'] = 'review'
        result['priority'] = 0
        result['reason'] = 'Urgent/action required - needs manual review'
        return result

    # Internal emails - always review
    if 'multifi.ai' in domain:
        result['category'] = 'internal'
        result['action'] = 'review'
        result['priority'] = 1
        result['reason'] = 'Internal email - needs review'
        return result

    # Newsletters - auto archive
    newsletter_domains = ['substack.com', 'medium.com', 'beehiiv.com', 'convertkit.com']
    if any(d in domain for d in newsletter_domains):
        result['category'] = 'newsletter'
        result['action'] = 'archive'
        result['priority'] = 5
        result['reason'] = 'Newsletter - auto archive'
        return result

    # LinkedIn notifications - auto archive
    if 'linkedin.com' in domain:
        if 'message' in subject or 'sent you' in subject:
            result['category'] = 'direct_message'
            result['action'] = 'review'
            result['priority'] = 2
            result['reason'] = 'LinkedIn direct message - needs review'
        else:
            result['category'] = 'notification'
            result['action'] = 'archive'
            result['priority'] = 5
            result['reason'] = 'LinkedIn notification - auto archive'
        return result

    # Financial receipts - archive after noting
    if any(d in domain for d in ['stripe.com', 'mercury.com', 'bill.com', 'expensify.com']):
        if any(w in subject for w in ['invoice', 'receipt', 'payment', 'charge']):
            result['category'] = 'receipt'
            result['action'] = 'archive'
            result['priority'] = 4
            result['reason'] = 'Receipt - auto archive'
            return result

    # SaaS notifications - auto archive
    saas_domains = ['anthropic.com', 'claude.com', 'openai.com', 'supabase.com',
                    'vercel.com', 'github.com', 'notion.so']
    if any(d in domain for d in saas_domains):
        if not any(kw in subject for kw in urgent_keywords):
            result['category'] = 'saas_notification'
            result['action'] = 'archive'
            result['priority'] = 5
            result['reason'] = 'SaaS notification - auto archive'
            return result

    # Calendar invites - auto archive (assuming already responded in calendar)
    if 'calendar' in subject or 'invitation' in subject or 'invite' in subject:
        result['category'] = 'calendar'
        result['action'] = 'archive'
        result['priority'] = 4
        result['reason'] = 'Calendar invite - auto archive'
        return result

    return result


def archive_email(message_id):
    """Archive email via gmail API."""
    try:
        subprocess.run(
            ['python', 'batch_archive_remaining.py', '--message-ids', message_id],
            cwd=Path(__file__).parent,
            check=True,
            capture_output=True
        )
        return True
    except Exception as e:
        print(f"❌ Failed to archive {message_id}: {e}")
        return False


def save_review_list(emails, output_file):
    """Save emails requiring review to a file."""
    skill_dir = Path(__file__).parent
    review_file = skill_dir / output_file

    review_data = []
    for email in emails:
        review_data.append({
            'message_id': email['message_id'],
            'from': email['metadata']['from'],
            'subject': email['metadata']['subject'],
            'date': email['metadata']['date'],
            'snippet': email['snippet'][:200],
            'category': email['processing']['category'],
            'reason': email['processing']['reason'],
            'suggested_actions': email['processing'].get('suggested_actions', [])
        })

    with open(review_file, 'w') as f:
        yaml.dump({
            'review_date': datetime.now().isoformat(),
            'total_count': len(review_data),
            'emails_needing_review': review_data
        }, f, default_flow_style=False, allow_unicode=True)

    print(f"✅ Saved {len(review_data)} emails to review list: {review_file}")
    return review_file


def generate_trello_suggestions(email):
    """Generate suggested Trello actions for an email."""
    subject = email['metadata']['subject']
    from_addr = email['metadata']['from']

    suggestions = []

    # Default suggestion
    suggestions.append({
        'action': f"Review and respond to: {subject}",
        'due_days': 1
    })

    # Keyword-based suggestions
    subject_lower = subject.lower()

    if 'proposal' in subject_lower or 'contract' in subject_lower:
        suggestions.append({
            'action': f"Review {subject} - check terms and pricing",
            'due_days': 3
        })

    if 'meeting' in subject_lower or 'call' in subject_lower:
        suggestions.append({
            'action': f"Prepare for meeting: {subject}",
            'due_days': 1
        })

    if 'report' in subject_lower or 'analysis' in subject_lower:
        suggestions.append({
            'action': f"Review report: {subject}",
            'due_days': 2
        })

    return suggestions


def main():
    """Main automated processing logic."""
    print("=" * 80)
    print("🤖 AUTOMATED EMAIL PROCESSING")
    print("=" * 80)
    print("\nLoading emails...")

    emails = load_emails()

    if not emails:
        print("✨ No emails to process!")
        return

    print(f"✅ Loaded {len(emails)} emails")

    # Load processing rules
    rules = load_processing_rules()

    # Process and categorize all emails
    print("\n📊 Analyzing emails...")
    for email in emails:
        email['processing'] = categorize_email(email)

    # Sort by priority
    emails.sort(key=lambda e: e['processing']['priority'])

    # Stats
    stats = {
        'total': len(emails),
        'auto_archived': 0,
        'needs_review': 0,
        'needs_trello': 0,
        'errors': 0
    }

    to_review = []
    to_trello = []

    print("\n🔄 Processing emails...")
    print("-" * 80)

    for email in emails:
        action = email['processing']['action']
        category = email['processing']['category']

        print(f"\n📧 [{category.upper()}] {email['metadata']['subject'][:60]}")
        print(f"   From: {email['metadata']['from'][:50]}")
        print(f"   Action: {action} - {email['processing']['reason']}")

        if action == 'archive':
            if archive_email(email['message_id']):
                print("   ✅ Archived")
                stats['auto_archived'] += 1
            else:
                print("   ⚠️  Failed to archive - needs manual review")
                to_review.append(email)
                stats['errors'] += 1

        elif action == 'review':
            print("   👀 Needs manual review")
            to_review.append(email)
            stats['needs_review'] += 1

            # Add Trello suggestions for review items
            email['processing']['suggested_actions'] = generate_trello_suggestions(email)

        elif action == 'trello':
            print("   📋 Suggested for Trello card")
            to_trello.append(email)
            stats['needs_trello'] += 1
            email['processing']['suggested_actions'] = generate_trello_suggestions(email)

    # Save items needing review
    print("\n" + "=" * 80)
    print("💾 SAVING REVIEW LISTS")
    print("=" * 80)

    if to_review:
        review_file = save_review_list(to_review, str(Path(__file__).parent.parent / 'data' / 'emails_to_review.yaml'))
    else:
        print("✅ No emails need manual review!")

    if to_trello:
        save_review_list(to_trello, 'emails_for_trello.yaml')

    # Final summary
    print("\n" + "=" * 80)
    print("📊 PROCESSING SUMMARY")
    print("=" * 80)
    print(f"  Total emails: {stats['total']}")
    print(f"  ✅ Auto-archived: {stats['auto_archived']}")
    print(f"  👀 Needs review: {stats['needs_review']}")
    print(f"  📋 Suggested for Trello: {stats['needs_trello']}")
    print(f"  ⚠️  Errors: {stats['errors']}")
    print("=" * 80)

    if stats['needs_review'] > 0:
        print(f"\n📝 Next step: Review emails_to_review.yaml for {stats['needs_review']} items")
        print("   Use process_review_list.py to handle these emails")

    if stats['auto_archived'] == stats['total']:
        print("\n🎉 ALL EMAILS AUTO-PROCESSED! 🎉")
    else:
        print(f"\n💪 {stats['auto_archived']} emails processed automatically")
        print(f"   {stats['needs_review']} emails need your attention")


if __name__ == "__main__":
    main()
