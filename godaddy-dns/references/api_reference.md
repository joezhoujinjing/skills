# GoDaddy API v1 Reference

Base URL: `https://api.godaddy.com/v1`

## Authentication

All requests require the `Authorization` header:

```
Authorization: sso-key {API_KEY}:{API_SECRET}
```

## Rate Limits

- 60 requests per minute per API key

## Endpoints

### Domains

| Method | Endpoint          | Description        |
| ------ | ----------------- | ------------------ |
| GET    | /domains          | List all domains   |
| GET    | /domains/{domain} | Get domain details |

### DNS Records

| Method | Endpoint                                | Description             |
| ------ | --------------------------------------- | ----------------------- |
| GET    | /domains/{domain}/records               | List all records        |
| GET    | /domains/{domain}/records/{type}        | List records by type    |
| GET    | /domains/{domain}/records/{type}/{name} | Get specific record     |
| PATCH  | /domains/{domain}/records               | Add records (append)    |
| PUT    | /domains/{domain}/records               | Replace all records     |
| PUT    | /domains/{domain}/records/{type}        | Replace records of type |
| PUT    | /domains/{domain}/records/{type}/{name} | Replace specific record |
| DELETE | /domains/{domain}/records/{type}/{name} | Delete specific record  |

## Record Structure

```json
{
  "type": "A",
  "name": "@",
  "data": "192.168.1.1",
  "ttl": 3600,
  "priority": 10 // Only for MX, SRV
}
```

## Record Types

### A Record (IPv4)

```json
{ "type": "A", "name": "www", "data": "192.168.1.1", "ttl": 3600 }
```

### AAAA Record (IPv6)

```json
{ "type": "AAAA", "name": "www", "data": "2001:db8::1", "ttl": 3600 }
```

### CNAME Record (Alias)

```json
{ "type": "CNAME", "name": "blog", "data": "example.com", "ttl": 3600 }
```

### MX Record (Mail)

```json
{ "type": "MX", "name": "@", "data": "mail.example.com", "ttl": 3600, "priority": 10 }
```

### TXT Record

```json
{ "type": "TXT", "name": "@", "data": "v=spf1 include:_spf.google.com ~all", "ttl": 3600 }
```

### NS Record (Nameserver)

```json
{ "type": "NS", "name": "@", "data": "ns1.example.com", "ttl": 3600 }
```

### SRV Record (Service)

```json
{
  "type": "SRV",
  "name": "_sip._tcp",
  "data": "sipserver.example.com",
  "ttl": 3600,
  "priority": 10,
  "weight": 5,
  "port": 5060
}
```

### CAA Record

```json
{ "type": "CAA", "name": "@", "data": "0 issue \"letsencrypt.org\"", "ttl": 3600 }
```

## Common Error Codes

| Code | Message                 |
| ---- | ----------------------- |
| 401  | Authentication required |
| 403  | Access denied           |
| 404  | Domain/record not found |
| 422  | Invalid record data     |
| 429  | Rate limit exceeded     |

## Example cURL Commands

### List domains

```bash
curl -X GET "https://api.godaddy.com/v1/domains" \
  -H "Authorization: sso-key {KEY}:{SECRET}"
```

### List DNS records

```bash
curl -X GET "https://api.godaddy.com/v1/domains/example.com/records" \
  -H "Authorization: sso-key {KEY}:{SECRET}"
```

### Add record

```bash
curl -X PATCH "https://api.godaddy.com/v1/domains/example.com/records" \
  -H "Authorization: sso-key {KEY}:{SECRET}" \
  -H "Content-Type: application/json" \
  -d '[{"type":"A","name":"www","data":"192.168.1.1","ttl":3600}]'
```

### Update record

```bash
curl -X PUT "https://api.godaddy.com/v1/domains/example.com/records/A/www" \
  -H "Authorization: sso-key {KEY}:{SECRET}" \
  -H "Content-Type: application/json" \
  -d '[{"data":"192.168.1.2","ttl":3600}]'
```

### Delete record

```bash
curl -X DELETE "https://api.godaddy.com/v1/domains/example.com/records/A/www" \
  -H "Authorization: sso-key {KEY}:{SECRET}"
```
