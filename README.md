# Insighta Labs+ API Documentation

Complete API reference for Insighta Labs+ Platform.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.insighta.io`

## API Versions

All endpoints support versioning via URL path:
- V1 (Legacy): `/api/v1/...`
- V2 (Current): `/api/v2/...`

## Authentication

### OAuth Flow with PKCE

#### 1. Initiate Login

```http
GET /auth/github/login/
```

**Browser redirect** to GitHub OAuth authorize URL.

Response: HTTP redirect to GitHub

---

#### 2. GitHub Callback

```http
GET /auth/github/callback/?code=AUTH_CODE
```

**Parameters:**
- `code`: GitHub authorization code

**Response (200 OK):**
```json
{
  "status": "success"
}
```

**Cookies Set:**
- `access_token` (HTTP-only, 10 min expiry)
- `refresh_token` (HTTP-only, 7 day expiry)

---

#### 3. CLI Token Exchange

```http
POST /auth/github/token/
Content-Type: application/json

{
  "code": "github_authorization_code",
  "code_verifier": "pkce_code_verifier"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "019db06d-c71c-7000-9c00-000000000001",
    "email": "user@github.local",
    "username": "github_username",
    "role": "analyst",
    "is_verified": true,
    "is_active": true,
    "created_at": "2026-04-29T10:00:00Z",
    "updated_at": "2026-04-29T10:00:00Z",
    "last_login_at": "2026-04-29T10:00:00Z"
  }
}
```

---

### Token Refresh

```http
POST /auth/token/refresh/
Content-Type: application/json

{
  "refresh": "refresh_token_string"
}
```

**Or with cookies:**
```http
POST /auth/token/refresh/
Cookie: refresh_token=...
```

**Response (200 OK):**
```json
{
  "status": "success",
  "access": "new_access_token",
  "refresh": "new_refresh_token"
}
```

---

### Logout

```http
POST /auth/logout/
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json

{
  "refresh": "refresh_token_string"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

**Cookies Cleared:**
- `access_token`
- `refresh_token`

---

### Get Current User

```http
GET /auth/me/
Authorization: Bearer ACCESS_TOKEN
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "019db06d-c71c-7000-9c00-000000000001",
    "email": "user@example.com",
    "username": "john_doe",
    "github_username": "john_doe_github",
    "role": "analyst",
    "is_active": true,
    "is_verified": true,
    "created_at": "2026-04-29T10:00:00Z",
    "updated_at": "2026-04-29T10:00:00Z",
    "last_login_at": "2026-04-29T10:00:00Z"
  }
}
```

---

## Profiles

### List Profiles

```http
GET /api/v2/profiles?page=1&limit=10
Authorization: Bearer ACCESS_TOKEN
```

**Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Results per page (default: 10, max: 50)
- `gender` (string): Filter by gender (male/female)
- `age_group` (string): Filter by age group (child/teenager/adult/senior)
- `country_id` (string): Filter by country code (e.g., NG, US)
- `min_age` (int): Minimum age filter
- `max_age` (int): Maximum age filter
- `min_gender_probability` (float): Minimum gender confidence (0-1)
- `min_country_probability` (float): Minimum country confidence (0-1)
- `sort_by` (string): Sort by field (age, created_at, gender_probability)
- `order_by` (string): Sort order (asc/desc, default: asc)

**Response (200 OK):**
```json
{
  "status": "success",
  "version": "v2",
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 42,
    "pages": 5,
    "has_next": true,
    "has_previous": false
  },
  "data": [
    {
      "id": "019db06d-b517-70dd-8746-8c1e039a8dc0",
      "name": "Thabo Ndebele",
      "gender": "male",
      "gender_probability": 0.66,
      "age": 18,
      "age_group": "teenager",
      "country_id": "AO",
      "country_name": "Angola",
      "country_probability": 0.68,
      "created_at": "2026-04-21T14:24:32.183559Z"
    }
  ]
}
```

**Errors:**
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Missing authentication
- `403 Forbidden`: Insufficient permissions

---

### Get Profile

```http
GET /api/v2/profiles/{id}
Authorization: Bearer ACCESS_TOKEN
```

**Parameters:**
- `id` (string, path): Profile UUID

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "019db06d-b517-70dd-8746-8c1e039a8dc0",
    "name": "Thabo Ndebele",
    "gender": "male",
    "gender_probability": 0.66,
    "age": 18,
    "age_group": "teenager",
    "country_id": "AO",
    "country_name": "Angola",
    "country_probability": 0.68,
    "created_at": "2026-04-21T14:24:32.183559Z"
  }
}
```

**Errors:**
- `404 Not Found`: Profile not found
- `401 Unauthorized`: Missing authentication

---

### Create Profile

```http
POST /api/v2/profiles
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json

{
  "name": "John Doe"
}
```

**Body Parameters:**
- `name` (string, required): Person's name (letters only)

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Profile created successfully",
  "data": {
    "id": "019db06d-b517-70dd-8746-8c1e039a8dc0",
    "name": "John Doe",
    "gender": "male",
    "gender_probability": 0.95,
    "age": 35,
    "age_group": "adult",
    "country_id": "US",
    "country_name": "United States",
    "country_probability": 0.85,
    "created_at": "2026-04-29T10:00:00Z"
  }
}
```

**Notes:**
- Queries genderize.io, agify.io, nationalize.io APIs
- Returns 400 if profile already exists
- Returns 502 if external API fails

**Errors:**
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing authentication
- `403 Forbidden`: Insufficient permissions
- `422 Unprocessable Entity`: Name contains non-alphabetic characters
- `502 Bad Gateway`: External API error

---

### Delete Profile

```http
DELETE /api/v2/profiles/{id}
Authorization: Bearer ACCESS_TOKEN
```

**Parameters:**
- `id` (string, path): Profile UUID

**Response (204 No Content)**

**Permission:**
- Admin role required
- Analyst role cannot delete

**Errors:**
- `401 Unauthorized`: Missing authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Profile not found

---

### Search Profiles

```http
GET /api/v2/profiles/search?q=female+adults+from+Nigeria
Authorization: Bearer ACCESS_TOKEN
```

**Parameters:**
- `q` (string, required): Natural language search query
- `page` (int): Page number (default: 1)
- `limit` (int): Results per page (default: 10)

**Query Examples:**
- "female" - All females
- "males" - All males
- "adults" - Age group 20-59
- "teenagers" - Age group 13-19
- "older than 25" - Age > 25
- "below 18" - Age < 18
- "from Nigeria" - Country = Nigeria
- "from age 5 to 12" - Age range 5-12
- "female adults from Nigeria" - Combined filters

**Response (200 OK):**
```json
{
  "status": "success",
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 5,
    "pages": 1,
    "has_next": false,
    "has_previous": false
  },
  "data": [...]
}
```

**Errors:**
- `400 Bad Request`: Unable to interpret query
- `401 Unauthorized`: Missing authentication
- `404 Not Found`: No results found

---

### Export Profiles

```http
GET /api/v2/profiles/export/csv?gender=male&country_id=NG
Authorization: Bearer ACCESS_TOKEN
```

**Parameters:**
- `gender` (string): Filter by gender
- `age_group` (string): Filter by age group
- `country_id` (string): Filter by country

**Response (200 OK):**
```
Content-Type: text/csv
Content-Disposition: attachment; filename="profiles_export.csv"

ID,Name,Gender,Gender Probability,Age,Age Group,Country ID,Country Name,Country Probability,Created At
019db06d-b517-70dd-8746-8c1e039a8dc0,John Doe,male,0.95,35,adult,US,United States,0.85,2026-04-29T10:00:00Z
...
```

**Permission:**
- Analyst role and above

**Errors:**
- `401 Unauthorized`: Missing authentication
- `403 Forbidden`: Insufficient permissions

---

## Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Successful GET/PUT request |
| 201 | Created | Successful POST request |
| 204 | No Content | Successful DELETE request |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal server error |
| 502 | Bad Gateway | External API error |

---

## Rate Limiting

All endpoints are rate limited to **100 requests per hour per IP**.

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1651244800
```

**Response on limit exceeded (429):**
```json
{
  "error": "Rate limit exceeded. Please try again later."
}
```

---

## CORS Headers

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, X-CSRFToken
```

---

## Security Headers

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

---

## Status Codes in Responses

### Success Response
```json
{
  "status": "success",
  "data": {...}
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Detailed error message",
  "code": "ERROR_CODE"
}
```

---

## Pagination Details

### V2 Pagination Metadata

```json
{
  "pagination": {
    "page": 1,           // Current page number
    "limit": 10,         // Items per page
    "total": 42,         // Total items
    "pages": 5,          // Total pages
    "has_next": true,    // More pages available
    "has_previous": false // Previous page available
  }
}
```

**Navigation:**
- First page: `page=1`
- Next page: `page=2`
- Last page: `page=5` (or `total_pages`)
- Previous page: `page=current-1`

---

## Timestamp Format

All timestamps use ISO 8601 format:
```
2026-04-29T14:24:32.183559Z
```

---

## Example: Full OAuth Flow (Web)

```javascript
// 1. Generate PKCE parameters
const codeVerifier = generateCodeVerifier();
const codeChallenge = await generateCodeChallenge(codeVerifier);

// 2. Redirect to GitHub
window.location.href = `
  https://github.com/login/oauth/authorize?
    client_id=${CLIENT_ID}&
    redirect_uri=${REDIRECT_URI}&
    scope=user&
    code_challenge=${codeChallenge}&
    code_challenge_method=S256
`;

// 3. Handle callback (in /auth/callback route)
const code = new URLSearchParams(window.location.search).get('code');

// 4. Server exchanges code for tokens
const response = await fetch(`${API_URL}/auth/github/token/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include', // Include cookies
  body: JSON.stringify({ code, code_verifier: codeVerifier })
});

// 5. Tokens stored in HTTP-only cookies automatically
// 6. Make authenticated requests with cookies
const profiles = await fetch(`${API_URL}/api/v2/profiles`, {
  credentials: 'include'
});
```

---

## Example: Full OAuth Flow (CLI)

```bash
# 1. User runs login command
insighta login

# 2. CLI generates PKCE parameters
# 3. Opens browser for authorization
# 4. CLI waits for callback on localhost:8888
# 5. User authorizes in browser
# 6. Browser redirects to localhost:8888?code=...
# 7. CLI exchanges code for tokens
# 8. Stores tokens in ~/.insighta/credentials.json

# 9. User can now make API requests
insighta profile list
insighta profile get <id>
insighta profile search "adults"
```

---

## Troubleshooting

### "Unauthorized" Error

**Cause**: Invalid or expired access token

**Solution**:
- Token expired: Call refresh endpoint
- Token missing: Ensure Authorization header is set
- Web: Check cookies are being sent with `credentials: 'include'`
- CLI: Re-login with `insighta login`

### "Rate Limited" Error

**Cause**: More than 100 requests per hour from your IP

**Solution**:
- Wait 1 hour
- Cache responses when possible
- Use pagination to reduce request count

### "CORS Error"

**Cause**: Request from non-whitelisted origin

**Solution**:
- Add your frontend URL to `CORS_TRUSTED_ORIGINS`
- Check `Access-Control-Allow-Origin` header

### 404 Profile Not Found

**Cause**: Profile ID doesn't exist or was deleted

**Solution**:
- Check profile ID is correct
- List profiles to find ID
- Deleted profiles cannot be recovered

---

## SDK Support

### Python
```python
from insighta_cli.api_client import APIClient

client = APIClient('http://localhost:8000', access_token='...')
profiles = client.get_profiles(page=1, limit=10)
profile = client.get_profile('profile-id')
client.search_profiles('female adults')
```

### JavaScript/TypeScript
```javascript
const api = new InsightaAPI('http://localhost:8000', accessToken);
const profiles = await api.getProfiles({ page: 1, limit: 10 });
const profile = await api.getProfile('profile-id');
const results = await api.searchProfiles('female adults');
```

---

## Support

For API issues:
1. Check error response message
2. Verify authentication token is valid
3. Check rate limiting headers
4. Review logs at `/logs/insighta.log`
5. Open GitHub issue with error details
