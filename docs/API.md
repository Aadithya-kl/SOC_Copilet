# SOC Copilot API Documentation (RC1)

This document provides a comprehensive overview of the RESTful API endpoints and WebSocket channels available in the SOC Copilot backend.

## Base URL
`http://localhost:8000/api/v1`

---

## 1. Authentication
*All endpoints (except login) require a valid JWT bearer token.*

### POST `/auth/login`
Authenticate a user and return a JWT.

**Request:**
```json
{
  "username": "admin",
  "password": "securepassword"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### POST `/auth/logout`
Invalidates the current token.

---

## 2. Incidents

### GET `/incidents`
Retrieve a paginated list of active and resolved incidents.

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "inc-9842",
      "severity": "CRITICAL",
      "status": "OPEN",
      "title": "Ransomware lateral movement detected",
      "created_at": "2026-06-30T10:00:00Z"
    }
  ],
  "total": 1
}
```

### GET `/incidents/{incident_id}`
Retrieve details for a specific incident.

### PATCH `/incidents/{incident_id}/status`
Update the status of an incident (e.g., OPEN, IN_PROGRESS, RESOLVED).

---

## 3. Investigations

### POST `/investigations`
Start a new AI-driven investigation for a specific incident.

**Request:**
```json
{
  "incident_id": "inc-9842",
  "priority": "HIGH"
}
```

**Response (201 Created):**
```json
{
  "investigation_id": "inv-105",
  "status": "STARTED",
  "assigned_ai_agent": "copilot-alpha"
}
```

### GET `/investigations/{investigation_id}`
Retrieve the current state and findings of an investigation.

---

## 4. Uploads

### POST `/uploads/pcap`
Upload a PCAP file for deep packet inspection and correlation.

**Request (Multipart/form-data):**
`file: [binary data]`

**Response (202 Accepted):**
```json
{
  "upload_id": "upl-401",
  "status": "PROCESSING",
  "message": "PCAP queued for analysis."
}
```

### POST `/uploads/logs`
Upload raw log files (e.g., syslog, Windows Event Logs).

---

## 5. Threat Intelligence

### GET `/threat-intel/indicators`
Lookup an Indicator of Compromise (IoC) against connected threat feeds.

**Request (Query parameters):**
`?value=185.15.20.12&type=ip`

**Response (200 OK):**
```json
{
  "ioc": "185.15.20.12",
  "malicious": true,
  "confidence": 95,
  "tags": ["cobalt-strike", "c2"]
}
```

---

## 6. Evidence

### POST `/evidence`
Attach a piece of evidence (file, log snippet, registry key) to an investigation.

**Request:**
```json
{
  "investigation_id": "inv-105",
  "evidence_type": "REGISTRY_KEY",
  "data": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\Malware"
}
```

### GET `/investigations/{investigation_id}/evidence`
Retrieve all evidence collected for a specific investigation.

---

## 7. Correlation

### POST `/correlation/analyze`
Force a correlation run across multiple evidence points to find hidden links.

**Request:**
```json
{
  "evidence_ids": ["ev-10", "ev-11", "ev-15"]
}
```

**Response (200 OK):**
```json
{
  "correlation_id": "corr-99",
  "findings": [
    "Both IPs map to the same autonomous system known for bulletproof hosting."
  ]
}
```

---

## 8. Timeline

### GET `/investigations/{investigation_id}/timeline`
Retrieve a chronologically ordered sequence of events related to an investigation.

**Response (200 OK):**
```json
[
  {
    "timestamp": "2026-06-30T09:15:00Z",
    "event_type": "INITIAL_ACCESS",
    "description": "Phishing email clicked by user."
  },
  {
    "timestamp": "2026-06-30T09:17:30Z",
    "event_type": "EXECUTION",
    "description": "Malicious payload downloaded."
  }
]
```

---

## 9. Graph

### GET `/graph/nodes`
Retrieve the knowledge graph representation of an incident (nodes and edges) for visual rendering in the frontend.

**Response (200 OK):**
```json
{
  "nodes": [
    {"id": "n1", "label": "10.0.0.5", "type": "Host"},
    {"id": "n2", "label": "evil.com", "type": "Domain"}
  ],
  "edges": [
    {"source": "n1", "target": "n2", "label": "DNS_REQUEST"}
  ]
}
```

---

## 10. MITRE

### GET `/mitre/tactics/{incident_id}`
Map current incident findings to the MITRE ATT&CK framework.

**Response (200 OK):**
```json
{
  "tactics": [
    {
      "id": "TA0001",
      "name": "Initial Access",
      "techniques": ["T1566 - Phishing"]
    }
  ]
}
```

---

## 11. AI

### POST `/ai/summarize`
Request the AI Copilot to summarize a dense log file or block of text.

**Request:**
```json
{
  "content": "[Raw syslog data...]",
  "format": "bullet_points"
}
```

**Response (200 OK):**
```json
{
  "summary": "- Unauthorized SSH attempt from 192.168.1.50\n- Privilege escalation via sudo"
}
```

---

## 12. Reports

### POST `/reports/generate`
Generate a PDF or Markdown report for a resolved incident.

**Request:**
```json
{
  "incident_id": "inc-9842",
  "format": "pdf",
  "include_evidence": true
}
```

**Response (200 OK):**
```json
{
  "report_url": "/downloads/reports/inc-9842-final.pdf"
}
```

---

## 13. Chat

### POST `/chat/message`
Send a message to the AI SOC Copilot for interactive querying.

**Request:**
```json
{
  "session_id": "chat-001",
  "message": "What is the blast radius of the compromised host?"
}
```

**Response (200 OK):**
```json
{
  "reply": "Based on the network traffic analysis, the host 10.0.0.5 communicated with 3 other internal servers via SMB after the initial infection.",
  "sources": ["ev-12", "ev-14"]
}
```

---

## 14. WebSockets

### WS `/ws/live-feed`
Subscribe to real-time alerts and state changes.

**Client Message (Subscribe):**
```json
{
  "action": "subscribe",
  "channel": "incidents"
}
```

**Server Message (Event):**
```json
{
  "event": "NEW_INCIDENT",
  "data": {
    "id": "inc-9843",
    "severity": "HIGH"
  }
}
```
