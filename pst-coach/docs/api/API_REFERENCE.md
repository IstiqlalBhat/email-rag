# API Reference

## Base URL
```
Development: http://localhost:8000/api
Production: https://api.pstcoach.example.com/api
```

## Authentication

All endpoints except `/auth/login` and `/auth/signup` require authentication via JWT Bearer token.

```http
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### POST /auth/signup
Register a new user and tenant.

#### POST /auth/login
Authenticate and receive JWT tokens.

#### POST /auth/logout
Invalidate current session.

#### GET /auth/me
Get current user information.

### Uploads

#### POST /uploads/presign
Generate presigned S3 URLs for multipart upload.

#### POST /uploads/complete
Complete upload and trigger processing.

#### GET /uploads/{upload_id}
Get upload status.

### Jobs

#### GET /jobs/{job_id}
Get job status and progress.

#### POST /jobs/{job_id}/cancel
Cancel a running job.

### Mailboxes

#### GET /mailboxes/{id}/overview
Get mailbox summary.

#### GET /mailboxes/{id}/metrics
Get specific metrics data.

#### GET /mailboxes/{id}/insights
Get insight artifacts.

### Chat

#### POST /chat/ask
Ask My Inbox mode - factual RAG.

#### POST /chat/coach
Coach Me mode - insights and coaching.

### Privacy

#### GET /privacy/settings
Get privacy settings.

#### PUT /privacy/settings
Update privacy settings.

#### POST /privacy/delete
Request data deletion.

For detailed request/response schemas, see inline API documentation at `/api/docs`.
