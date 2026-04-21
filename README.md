# BlastHub
What happens when the processing system has too many things to process? Poorly designed systems fail under burst traffic, leading to downtime, data loss, and uncontrolled costs. Let's try reducing the blast radius with this project.

# Burst-Tolerant File Processing System (AWS)

## Problem Statement

Poorly designed systems fail under burst traffic, leading to:
- downtime
- data loss
- uncontrolled costs

This project demonstrates how to design a system that can **handle sudden spikes reliably** while remaining cost-efficient.

---

## System Overview

Users upload files which are processed asynchronously. The system:
- absorbs spikes using a queue
- scales compute automatically
- tracks processing status reliably

---

## Architecture Diagram

<img width="808" height="625" alt="image" src="https://github.com/user-attachments/assets/b3c39a15-758f-44e5-9b28-6e1baae072f4" />


---

## System Flow

1. User authenticates
2. User requests upload → backend generates pre-signed URL + job ID
3. User uploads file directly to storage
4. Storage triggers event → message sent to queue
5. Compute service pulls message from queue
6. File is processed (resize/compress/etc.)
7. Processed file stored back in storage
8. Job status updated in database
9. User fetches status or downloads result

---

## Key Design Decisions

### Pre-Signed URLs
- Offloads upload traffic from backend
- Improves scalability
- Reduces cost

### Asynchronous Processing
- Prevents system failure during traffic spikes
- Queue buffers incoming load

### Standard Queue (Not FIFO)
- High throughput for burst handling
- Ordering not required
- Handles duplicate messages via idempotency

### Serverless Compute
- Auto-scales with demand
- No idle cost

### Database for State Tracking
- Stores job status (pending, processing, completed, failed)
- Enables user status queries

### No VPC (Intentional)
- All services are managed
- Avoids unnecessary cost and complexity
- VPC only needed for private resources like databases

---

## Failure Handling

- Retry with exponential backoff
- Dead Letter Queue (DLQ) for repeated failures
- Idempotent processing using job IDs

---

## Cost Considerations

- No always-on servers
- Pay-per-use compute
- Storage and processing decoupled

---

## Security

- Authentication via Cognito
- Private storage (no public access)
- Pre-signed URLs for secure upload/download
- Least-privilege IAM roles

---

## Future Improvements

- Use containers for sustained workloads
- Add caching layer
- Add monitoring and alerting
- Introduce rate limiting

---

## Tech Stack

- Amazon S3
- Amazon SQS
- AWS Lambda
- Amazon DynamoDB
- Amazon Cognito
- API Gateway

---

## What This Project Demonstrates

- Handling burst traffic
- Event-driven architecture
- Fault-tolerant design
- Cost-aware system building
