---
name: trello
description: Manage Trello boards, lists, and cards via the Trello REST API.
homepage: https://developer.atlassian.com/cloud/trello/rest/
metadata:
  {
    "clawdbot":
      { "emoji": "📋", "requires": { "bins": ["jq"], "env": ["TRELLO_API_KEY", "TRELLO_TOKEN"] } },
  }
---

# Trello Skill

Manage Trello boards, lists, and cards via Trello REST API.

## Setup

1. Get API key: https://trello.com/app-key
2. Generate token (click "Token" link)
3. Store in Secret Manager: `/secret-vault set trello-api-key "key"` and `/secret-vault set trello-token "token"`

## Usage

Retrieve credentials first:

```bash
TRELLO_API_KEY=$(gcloud secrets versions access latest --secret="trello-api-key")
TRELLO_TOKEN=$(gcloud secrets versions access latest --secret="trello-token")
```

### Boards

```bash
# List boards
curl -s "https://api.trello.com/1/members/me/boards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id, url}'

# Create board
curl -s -X POST "https://api.trello.com/1/boards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" -d "name=Board Name" | jq '{name, id, url}'

# Share board (invite by email)
curl -s -X PUT "https://api.trello.com/1/boards/{boardId}/members?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" -d "email=user@example.com" -d "type=normal"

# List board members
curl -s "https://api.trello.com/1/boards/{boardId}/members?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {fullName, username, email}'
```

### Lists

```bash
# List lists in board
curl -s "https://api.trello.com/1/boards/{boardId}/lists?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id}'
```

### Cards

```bash
# List cards in list
curl -s "https://api.trello.com/1/lists/{listId}/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id, desc}'

# Create card
curl -s -X POST "https://api.trello.com/1/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" -d "idList={listId}" -d "name=Title" -d "desc=Description"

# Update card
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" -d "name=Title" -d "desc=Description"

# Move card
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" -d "idList={newListId}"

# Archive card
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" -d "closed=true"

# Delete card
curl -s -X DELETE "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"

# Add comment
curl -s -X POST "https://api.trello.com/1/cards/{cardId}/actions/comments?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" -d "text=Comment"
```

## Notes

- IDs found in Trello URLs or via list commands
- Rate limits: 300 req/10s per API key; 100 req/10s per token
