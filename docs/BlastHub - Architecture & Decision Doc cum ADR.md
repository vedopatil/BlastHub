# Project Documentation: Burst-Resilient Async Processor

### 1. Problem Statement

* **Burst uploads** – The system must handle burst uploads where thousands of files may arrive in a short time window. It must process these files asynchronously without blocking user requests, ensure no data loss, and operate within a constrained budget. The system should remain stable under sudden spikes while allowing eventual completion of all processing jobs.  
* **Async processing** – Decoupled architecture ensures there is no dependency on whether the previous or next processing job fails.  
* **Cost constraint** – A simulated budget of 10k/month is the upper bound, but this shouldn’t exceed the burst cost spikes, which are managed within this limit.  
* **No data loss** – The core requirement: zero data loss and guaranteed processing for every job.

---

### 2. System Flow

**Step-by-step:** Auth → URL → Job creation → Upload → Event → Queue → Compute → Store → Status  

This flow ensures clarity before building. Here’s the architectural visualization:  

<img width="808" height="625" alt="image" src="https://github.com/user-attachments/assets/b3c39a15-758f-44e5-9b28-6e1baae072f4"/>

---

### 3. Key Decisions

#### Decision 1: Pre-signed URLs
* **Why:** Removes backend bottleneck by allowing direct-to-storage uploads.
* **Trade-off:** Requires client-side validation and expiry handling.

#### Decision 2: SQS Standard (not FIFO)
* **Why:** Provides high throughput necessary for bursts.
* **Trade-off:** SQS acts as a buffer to absorb burst traffic and decouple ingestion from processing, preventing system overload during spikes.

#### Decision 3: Lambda
* **Why:** Offers burst scalability with no idle costs.
* **Trade-off:** Lambda is chosen for burst scalability and cost efficiency. However, it is constrained by execution limits (~15 minutes), making it unsuitable for long-running or CPU-intensive workloads.

#### Decision 4: No VPC
* **Why:** Utilizes fully managed services.
* **Trade-off:** A VPC is intentionally avoided since all services are managed and do not require private networking. Introducing a VPC would add unnecessary cost (e.g., NAT Gateway) and operational complexity without meaningful benefit.

#### Decision 5: DynamoDB
* **Why:** Fast, scalable state tracking. DynamoDB is used to track job lifecycle (pending, processing, completed, failed), enabling observability and idempotent processing.
* **Trade-off:** Requires consideration of eventual consistency.

#### Decision 6: Cognito
* Used for user authentication.
* Manages authorization; each request includes an auth token, allowing the backend to securely generate URLs only for authorized users.
* Supports Google, Apple, Meta, and custom sign-ups, providing flexibility at any scale.

#### Decision 7: S3
* Chosen as a resilient storage solution that stays within cost limits for storing files to be processed.
* Scales irrespective of load; as the system assumes burst scenarios, storage is the last component we want to fail. Options like EBS or Instance Store were ruled out.
* More cost-efficient than RDS or DocumentDB and provides greater flexibility for a large variety of file types.

#### Decision 8: API & API Gateway
* Provides a single point of access without exposing the entire backend.
* API Gateway allows for the design and management of different API types.

---

### 4. Failure Handling

* **Retry strategy:** Messages are retried using exponential backoff.
* **Dead Letter Queue:** Failed messages are moved to a DLQ after reaching the retry threshold.
* **Idempotency approach:** Processing is idempotent using job IDs to prevent duplicate execution.
* **Visibility timeout:** Ensures failed workers do not lose messages by making them visible in the queue again after a timeout.

---

### 5. Cost Thinking

* The system is designed so that compute scales with actual workload while the queue absorbs burst traffic, preventing uncontrolled concurrency and cost spikes.
* Lambda prevents wasted costs on idle servers.
* S3 events reduce management overhead and avoid the extra costs associated with EventBridge.

**Assumptions:**
* 1,000 users/day
* 2 files per user
* Total: 2,000 files/day
* Avg processing time: 5 seconds
* Lambda memory: 512 MB

**Lambda Math:**
* Pricing: ~$0.0000167 per GB-second
* 0.5 GB × 5 sec = 2.5 GB-sec per request
* 2,000 requests → 5,000 GB-sec/day
* **Daily Cost:** ~$0.083
* **Monthly Cost:** ~$2.50

**Additional Costs:**
* **S3 Storage:** (Approx 50GB) → ~$1–2/month
* **SQS:** Practically negligible → ~$0.50 or less
* **DynamoDB:** Low R/W metadata → ~$1–3/month

**Total Realistic Cost:** ~$5–10/month  
*Scaling example: 200,000 files/day → ~$350/month.*

---

### 6. What we are NOT solving

This system is intentionally scoped for burst ingestion and asynchronous processing. It does not address:
* Real-time or synchronous processing
* Multi-region redundancy
* Long-term storage optimization
* Domain-specific processing logic
* Advanced authorization models

---

### 7. Observability

* **Logs:** Capture processing steps and failures.
* **Metrics:** Monitor queue depth and processing latency.
* **Alerts:** Trigger notifications on DLQ growth or failure spikes.
