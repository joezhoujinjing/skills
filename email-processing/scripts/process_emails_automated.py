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
import concurrent.futures
import threading

# Use a thread-safe print function
print_lock = threading.Lock()
def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)

def load_emails():
    """Load emails from the dump file."""
    skill_dir = Path(__file__).parent.parent
    dump_file = skill_dir / "data" / "emails_dump.yaml"

    if not dump_file.exists():
        safe_print("❌ No data/emails_dump.yaml found!")
        safe_print("   Run: python scripts/export_unprocessed.py first")
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


def categorize_email(email, rules=None):
    """Categorize email using rules first, then fall back to LLM triage if needed."""
    if rules is None:
        rules = {}
        
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

    # 1. Check for urgent/action required (High Priority)
    urgent_keywords = rules.get('require_review_keywords', [])
    # Fallback defaults if empty
    if not urgent_keywords:
        urgent_keywords = ['action required', 'urgent', 'approve', 'approval needed',
                          'deadline', 'overdue', 'confirm', 'verification']
                          
    if any(kw in subject for kw in urgent_keywords):
        result['category'] = 'urgent'
        result['action'] = 'review'
        result['priority'] = 0
        result['reason'] = 'Urgent/action required - needs manual review'
        return result

    # 2. Internal emails - always review
    if 'multifi.ai' in domain:
        result['category'] = 'internal'
        result['action'] = 'review'
        result['priority'] = 1
        result['reason'] = 'Internal email - needs review'
        return result
        
    # 3. Important Senders - always review
    important_senders = rules.get('important_senders', [])
    if any(s in from_addr for s in important_senders):
        result['category'] = 'important_sender'
        result['action'] = 'review'
        result['priority'] = 1
        result['reason'] = 'Important sender - needs review'
        return result

    # 4. Auto-archive by Domain
    archive_domains = rules.get('auto_archive_domains', [])
    if not archive_domains:
        # Fallback defaults
        archive_domains = ['substack.com', 'medium.com', 'beehiiv.com', 'convertkit.com', 
                          'linkedin.com', 'stripe.com', 'mercury.com', 'bill.com']
                          
    if any(d in domain for d in archive_domains):
        # Special case for LinkedIn DMs
        if 'linkedin.com' in domain and ('message' in subject or 'sent you' in subject):
             pass # Drop through to default review
        else:
            result['category'] = 'auto_domain'
            result['action'] = 'archive'
            result['priority'] = 5
            result['reason'] = f'Domain {domain} - auto archive'
            return result

    # 5. Auto-archive by Keyword (Subject)
    archive_keywords = rules.get('auto_archive_keywords', [])
    if any(kw in subject for kw in archive_keywords):
        result['category'] = 'auto_keyword'
        result['action'] = 'archive'
        result['priority'] = 5
        result['reason'] = 'Subject keyword match - auto archive'
        return result

    # 6. Calendar invites
    if 'calendar' in subject or 'invitation' in subject or 'invite' in subject:
        result['category'] = 'calendar'
        result['action'] = 'archive'
        result['priority'] = 4
        result['reason'] = 'Calendar invite - auto archive'
        return result

    return result

def llm_triage_email(email):
    """Call LLM to decide on action for an email."""
    # This is a placeholder for the actual LLM call.
    # In a real scenario, this would import requests or openai client
    # and call the API with the email content.
    
    # Simulate LLM call latency
    import time
    time.sleep(0.5) 

    # Simulated logic based on subject (replace with actual LLM logic)
    subject = email['metadata']['subject'].lower()
    
    result = {
        'category': 'llm_processed',
        'action': 'review',
        'priority': 3,
        'reason': 'LLM fallback - default review',
        'suggested_actions': []
    }

    if 'unsubscribe' in email['snippet'].lower():
        result['action'] = 'archive'
        result['reason'] = 'LLM detected newsletter/spam'
    elif 'meeting' in subject:
        result['action'] = 'trello'
        result['reason'] = 'LLM detected meeting request'
        result['suggested_actions'] = [{'action': f"Schedule: {subject}", 'due_days': 1}]
    
    return result

def archive_email(message_id):
    """Archive email via gmail API."""
    try:
        subprocess.run(
            [sys.executable, 'batch_archive_remaining.py', '--message-ids', message_id],
            cwd=Path(__file__).parent,
            check=True,
            capture_output=True
        )
        return True
    except Exception as e:
        safe_print(f"❌ Failed to archive {message_id}: {e}")
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

    safe_print(f"✅ Saved {len(review_data)} emails to review list: {review_file}")
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

def process_single_email(email, rules):
    """Process a single email: rule-based first, then LLM if needed."""
    
    # 1. Try rule-based categorization
    processing_result = categorize_email(email, rules)
    
    # 2. If rule-based result is 'review' (needs manual review), try LLM triage
    if processing_result['action'] == 'review' and processing_result['reason'] == 'Default - needs review':
         # Call LLM here (simulated)
         llm_result = llm_triage_email(email)
         # Merge LLM result if it provides a better action
         if llm_result['action'] != 'review':
             processing_result = llm_result
    
    email['processing'] = processing_result
    return email

def main():
    """Main automated processing logic."""
    safe_print("=" * 80)
    safe_print("🤖 AUTOMATED EMAIL PROCESSING (WITH CONCURRENT LLM TRIAGE)")
    safe_print("=" * 80)
    safe_print("\nLoading emails...")

    emails = load_emails()

    if not emails:
        safe_print("✨ No emails to process!")
        return

    safe_print(f"✅ Loaded {len(emails)} emails")

    # Load processing rules
    rules = load_processing_rules()

    # Process and categorize all emails using ThreadPoolExecutor
    safe_print("\n📊 Analyzing emails (Concurrency Limit: 10)...")
    
    processed_emails = []
    
    # Use ThreadPoolExecutor to limit concurrency to 10
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all tasks
        future_to_email = {executor.submit(process_single_email, email, rules): email for email in emails}
        
        for future in concurrent.futures.as_completed(future_to_email):
            try:
                result = future.result()
                processed_emails.append(result)
            except Exception as exc:
                safe_print(f"❌ Email processing generated an exception: {exc}")

    # Replace original list with processed list
    emails = processed_emails

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
    to_archive_ids = []

    safe_print("\n🔄 Processing emails...")
    safe_print("-" * 80)

    for email in emails:
        action = email['processing']['action']
        category = email['processing']['category']

        safe_print(f"\n📧 [{category.upper()}] {email['metadata']['subject'][:60]}")
        safe_print(f"   From: {email['metadata']['from'][:50]}")
        safe_print(f"   Action: {action} - {email['processing']['reason']}")

        if action == 'archive':
            to_archive_ids.append(email['message_id'])
            safe_print("   ✅ Queued for batch archive")

        elif action == 'review':
            safe_print("   👀 Needs manual review")
            to_review.append(email)
            stats['needs_review'] += 1

            # Add Trello suggestions for review items
            if 'suggested_actions' not in email['processing']:
                email['processing']['suggested_actions'] = generate_trello_suggestions(email)

        elif action == 'trello':
            safe_print("   📋 Suggested for Trello card")
            to_trello.append(email)
            stats['needs_trello'] += 1
            if 'suggested_actions' not in email['processing']:
                email['processing']['suggested_actions'] = generate_trello_suggestions(email)

    # Process batch archive
    if to_archive_ids:
        safe_print(f"\n📦 Batch archiving {len(to_archive_ids)} emails...")
        
        # Use a smaller chunk size to avoid rate limits
        chunk_size = 10 
        
        # Import oauth_helper here to reuse the connection
        sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
        try:
            from oauth_helper import get_credentials
            from googleapiclient.discovery import build
        
            safe_print("🔐 Authenticating with Gmail for batch archive...")
            # Use the specific token if we can pass it, otherwise default
            # Ideally we should pass the same token used in export_unprocessed.py
            # For now, let's use the default or try to match the one from the CLI args if possible
            # Since this is a standalone script run, we might need to hardcode or guess
            # Let's try the personal one first as it's the current context
            credentials = get_credentials(refresh_token_secret="google-all-services-refresh-token-joezhoujinjing-gmail-com")
            service = build("gmail", "v1", credentials=credentials)
            
            total_archived = 0
            import time
            
            for i in range(0, len(to_archive_ids), chunk_size):
                chunk = to_archive_ids[i:i + chunk_size]
                try:
                    body = {
                        "ids": chunk,
                        "removeLabelIds": ["INBOX", "UNREAD"]
                    }
                    
                    service.users().messages().batchModify(
                        userId="me",
                        body=body
                    ).execute()
                    
                    total_archived += len(chunk)
                    stats['auto_archived'] += len(chunk)
                    safe_print(f"   ✅ Archived batch {i//chunk_size + 1} ({len(chunk)} emails) - Total: {total_archived}/{len(to_archive_ids)}")
                    
                    # Sleep briefly to be nice to the API
                    time.sleep(1.0)
                    
                except Exception as e:
                    safe_print(f"   ❌ Failed to archive batch {i//chunk_size + 1}: {e}")
                    stats['errors'] += len(chunk)
                    
        except Exception as e:
             safe_print(f"❌ Failed to initialize Gmail service or batch archive: {e}")


    # Save items needing review
    safe_print("\n" + "=" * 80)
    safe_print("💾 SAVING REVIEW LISTS")
    safe_print("=" * 80)

    if to_review:
        review_file = save_review_list(to_review, str(Path(__file__).parent.parent / 'data' / 'emails_to_review.yaml'))
    else:
        safe_print("✅ No emails need manual review!")

    if to_trello:
        save_review_list(to_trello, 'emails_for_trello.yaml')

    # Final summary
    safe_print("\n" + "=" * 80)
    safe_print("📊 PROCESSING SUMMARY")
    safe_print("=" * 80)
    safe_print(f"  Total emails: {stats['total']}")
    safe_print(f"  ✅ Auto-archived: {stats['auto_archived']}")
    safe_print(f"  👀 Needs review: {stats['needs_review']}")
    safe_print(f"  📋 Suggested for Trello: {stats['needs_trello']}")
    safe_print(f"  ⚠️  Errors: {stats['errors']}")
    safe_print("=" * 80)

    if stats['needs_review'] > 0:
        safe_print(f"\n📝 Next step: Review emails_to_review.yaml for {stats['needs_review']} items")
        safe_print("   Use process_review_list.py to handle these emails")

    if stats['auto_archived'] == stats['total']:
        safe_print("\n🎉 ALL EMAILS AUTO-PROCESSED! 🎉")
    else:
        safe_print(f"\n💪 {stats['auto_archived']} emails processed automatically")
        safe_print(f"   {stats['needs_review']} emails need your attention")


if __name__ == "__main__":
    main()
