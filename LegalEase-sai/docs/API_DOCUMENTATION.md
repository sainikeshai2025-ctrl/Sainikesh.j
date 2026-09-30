# LegalEase API Documentation

The LegalEase Backend is built using **FastAPI** and runs by default on `http://127.0.0.1:8000`.

---

## 1. Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check & service discovery |
| `GET` | `/status` | AI Core generator status |
| `POST` | `/generate` | Generate AI legal document |
| `GET` | `/docs` | Interactive Swagger UI |
| `GET` | `/redoc` | Interactive ReDoc UI |

---

## 2. Generate Legal Document (`POST /generate`)

### Request Headers
```http
Content-Type: application/json
```

### Request Body Schema (`DocumentRequest`)
```json
{
  "document_type": "string (Required - e.g., 'Freelance Work Contract', 'NDA')",
  "parties": "string (Required - e.g., 'Jane Doe (Provider), TechNova Inc. (Client)')",
  "terms": "string (Semicolon-separated terms & conditions)",
  "dates": "string (Effective Date - e.g., 'April 10, 2025')"
}
```

### Example Request (`curl`)
```bash
curl -X POST "http://127.0.0.1:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "document_type": "Freelance Work Contract",
       "parties": "Jane Doe (Service Provider), TechNova Inc. (Client)",
       "terms": "Payment within 30 days of invoice; Provider delivers work by deadline; Confidentiality maintained at all times; Either party may terminate with 15 days notice",
       "dates": "April 10, 2025"
     }'
```

### Example Response (`200 OK`)
```json
{
  "document": "FREELANCE WORK CONTRACT\n\nThis Freelance Work Contract (the \"Agreement\")...\n\nSECTION 1: PURPOSE AND DEFINITIONS...",
  "status": "success"
}
```

---

## 3. Healthcheck Endpoint (`GET /`)

### Response
```json
{
  "status": "online",
  "service": "LegalEase: AI-Powered Legal Document Generator API",
  "version": "1.0.0",
  "docs_url": "/docs",
  "endpoints": {
    "root": "/",
    "generate": "/generate (POST)",
    "status": "/status (GET)"
  }
}
```
