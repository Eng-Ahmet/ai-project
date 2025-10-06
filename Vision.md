# VisionGuard — Automated Threat Detection for Safe Monitoring

**VisionGuard** is a responsible computer-vision security system that detects potential threats (weapons, masks/face coverings used for concealment, and violent / fighting behavior), captures short evidence clips, applies privacy-preserving measures (face blurring), stores encrypted evidence, and surfaces human-reviewable alerts to a dashboard. The system is explicitly designed **not** to perform biometric identification or persistent tracking of individuals — instead it focuses on safe automated detection + human-in-the-loop verification and incident escalation.

---

## Table of contents
1. [Project Overview](#project-overview)  
2. [Key Features](#key-features)  
3. [Architecture](#architecture)  
4. [Tech Stack](#tech-stack)  
5. [Quick Start — Local (developer) Setup](#quick-start)  
6. [Configuration / Environment Variables](#configuration--environment-variables)  
7. [Usage Examples](#usage-examples)  
8. [Data Storage & Privacy](#data-storage--privacy)  
9. [Evaluation & Metrics](#evaluation--metrics)  
10. [Deployment](#deployment)  
11. [Contributing](#contributing)  
12. [Legal & Ethical Notice](#legal--ethical-notice)  
13. [License & Contact](#license--contact)

---

## Project Overview
VisionGuard processes live video streams (RTSP/IP cameras or recorded video) and runs lightweight object-detection and action-recognition models to identify likely security incidents (weapon visible, suspicious mask/covering, or violent actions). When a potential incident is detected:

- Detection must be confirmed over multiple frames to reduce false positives.
- The system captures a short clip and image snapshots.
- All saved artifacts are processed with face blurring by default.
- Evidence files are encrypted at rest.
- The system generates an alert in a web dashboard for human review.
- If an operator confirms, the system can notify the configured security contact (SMS / email / webhook).

VisionGuard is intended for scenarios where early automated warning is needed while preserving privacy and complying with regulations.

---

## Key Features
- Real-time object detection (weapons, masks) and simple action recognition (fight/violent motion).
- Temporal smoothing — detections require confirmation across several frames.
- Evidence capture: short encrypted video clips + blurred snapshots.
- Human-in-the-loop workflow: operator reviews alerts before escalation.
- Audit logs and access control (RBAC).
- Configurable retention policy and storage encryption.
- Modular architecture — easily swap or fine-tune models.

---

## Architecture
```
[Cameras / Video Files] --> [Frame Grabber] --> [Detector (YOLO)] --> [Temporal Filter / Action Recognition]
        --> [Evidence Processor (face blur + encrypt)] --> [Storage (object store + DB)]
        --> [Alert Queue] --> [Dashboard (Human review)]
        --> [When confirmed] --> [Notification Service (email/SMS/webhook)]
```

---

## Tech Stack (suggested)
- CV / Detection: Python, OpenCV, PyTorch, Ultralytics YOLO (v8) or equivalent
- Pose / Action: MediaPipe or lightweight 3D-CNN / TSN
- Backend: FastAPI or Flask
- Frontend: React / Next.js
- Storage: PostgreSQL (metadata), S3-compatible object store (encrypted clips)
- Queue (optional): Redis / RabbitMQ
- Edge hardware (optional): NVIDIA Jetson / Intel NCS2
- Containerization: Docker & docker-compose

---

## Quick Start — Local (developer) Setup

> Minimal local dev steps — adjust values for production.

1. Clone the repo:
```bash
git clone https://github.com/your-org/visionguard.git
cd visionguard
```

2. Create & activate a Python virtual environment:
```bash
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

3. Install dependencies:
```bash
pip install -r requirements.txt
# Example deps: opencv-python, ultralytics, fastapi, uvicorn, cryptography, sqlalchemy, boto3
```

4. Copy example env and edit:
```bash
cp .env.example .env
# Edit .env to configure camera URLs, DB, encryption key, S3
```

5. Run backend & worker:
```bash
# Run API
uvicorn visionguard.api:app --reload --host 0.0.0.0 --port 8000

# Run detection worker
python -m visionguard.worker.detector_worker --config config/dev.yaml
```

6. Open dashboard:
- Visit `http://localhost:3000` (or configured port) to view alerts and confirm/reject.

---

## Configuration / Environment Variables

Store secrets in `.env` (never commit keys):
```
DATABASE_URL=postgresql://user:pass@localhost:5432/visionguard
S3_ENDPOINT=http://localhost:9000
S3_BUCKET=visionguard-evidence
S3_ACCESS_KEY=MINIO_ACCESS_KEY
S3_SECRET_KEY=MINIO_SECRET_KEY

ENCRYPTION_KEY=base64:...   # Fernet / AES key, keep secure
ALERT_CALLBACK_WEBHOOK=https://example.com/alert
ADMIN_EMAIL=security@site.example
RETENTION_DAYS=30
```

Example `config/dev.yaml`:
```yaml
cameras:
  - id: cam-entrance
    name: "Entrance Lobby"
    rtsp: "rtsp://user:pass@192.168.1.10/stream"
detector:
  model_path: "models/yolov8n.pt"
  min_confidence: 0.4
  temporal_frames: 5
evidence:
  pre_seconds: 3
  post_seconds: 2
  blur_faces: true
  encrypt: true
```

---

## Usage Examples (APIs & CLI)

### Detection worker
```bash
python -m visionguard.worker.detector_worker --config config/dev.yaml
```

### Backend endpoints (FastAPI)
- `POST /api/alerts/confirm` — operator confirms an alert.
- `POST /api/alerts/reject` — operator rejects an alert.
- `GET  /api/alerts` — list pending alerts.
- `GET  /api/evidence/{id}` — download (authorized) encrypted evidence.

### Example DB alert entry
```json
{
  "id": "alert_001",
  "camera_id": "cam-entrance",
  "time": "2025-10-01T11:00:00Z",
  "type": "weapon",
  "confidence": 0.87,
  "evidence_path": "s3://visionguard-evidence/alert_20251001_001.enc",
  "status": "pending"
}
```

---

## Data Storage & Privacy
- **Face Blurring:** All stored snapshots and clips are processed with face blurring by default to avoid biometric identification.
- **Encryption:** Evidence files are encrypted at rest (AES / Fernet) and transferred over HTTPS.
- **Retention:** Default `RETENTION_DAYS=30`. Evidence is deleted after retention unless flagged for legal retention.
- **Access Control & Audit:** Dashboard access requires authenticated accounts with RBAC. Every evidence access is logged.
- **No Biometric Matching:** VisionGuard does **not** perform facial recognition or identity linking across cameras. Any request to add identification requires legal review.

---

## Evaluation & Metrics
Monitor and tune:
- Precision, Recall, F1 per class (weapon, mask, fight).
- False Alarm Rate (alarms/hour).
- Detection latency (ms).
- Mean time-to-confirm (operator response).
- Storage usage & retention compliance.

Collect validation clips from deployment-like cameras for fine-tuning.

---

## Deployment
- **Small-scale:** Workers on edge devices (Jetson) + backend server.
- **Scalable:** Kubernetes for workers, managed object store for clips.
- **Security checklist:** secret manager (Vault/AWS Secrets), TLS everywhere, hardened images, backups for DB and metadata.

---

## Contributing
1. Fork repo.
2. Create branch `feat/your-feature`.
3. Add tests for detection or API behavior.
4. Submit PR with description and testing steps.
5. Do not include secrets in commits.

---

## Legal & Ethical Notice
**Important:** VisionGuard deliberately avoids biometric identification to reduce privacy risks. Prior to deployment:

- Verify compliance with local/regional laws (e.g., GDPR in EU).
- Put visible CCTV signage where required.
- Establish retention & access policies approved by legal counsel.
- Train operators on privacy-preserving workflows.
- Consult legal counsel before integrating with law enforcement or identification workflows.

The project authors are not responsible for misuse. Use VisionGuard ethically and lawfully.

---

## License & Contact
- **License:** MIT (or pick appropriate license for your organization)
- **Maintainer / Contact:** security-team@example.com

---

### Next steps I can provide (choose one)
- Create a downloadable `README.md` file and give it here.
- Generate `docker-compose.yml`, `requirements.txt`, and a minimal FastAPI skeleton.
- Create a starter React dashboard skeleton.
- Provide an example detection-worker script ready to run with a sample camera/video.

