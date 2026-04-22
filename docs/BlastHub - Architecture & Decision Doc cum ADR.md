### **1\. Problem Statement (5–6 lines)**

* Burst uploads \- The system must handle burst uploads where thousands of files may arrive in a short time window. It must process these files asynchronously without blocking user requests, ensure no data loss, and operate within a constrained budget. The system should remain stable under sudden spikes while allowing eventual completion of all processing jobs.  
* Async processing, decoupled, so dependency on whether the last or next processing job fails  
* Cost constraint, a simulated budget of 10k/month is the upper bound, but this shouldn’t exceed the burst cost spikes, which are to be managed within this as well  
* No data loss, the very core of this project, no data loss, and no processing job left out.

---

### **2\. System Flow (your refined version)**

Step-by-step:  
##### Auth → URL → Job creation → Upload → Event → Queue → Compute → Store → Status  
##### This locks clarity before building.  
#### Here’s a clearer version:  
<img width="808" height="625" alt="image" src="https://github.com/user-attachments/assets/b3c39a15-758f-44e5-9b28-6e1baae072f4"/>

---

### **3\. Key Decisions (THIS is the most important section)**

#### **Decision 1: Pre-signed URLs**

* Why: removes backend bottleneck  
* Trade-off: requires validation \+ expiry handling

#### **Decision 2: SQS Standard (not FIFO)**

* Why: high throughput  
* Trade-off: SQS acts as a buffer to absorb burst traffic and decouple ingestion from processing, preventing system overload during spikes.

#### **Decision 3: Lambda**

* Why: burst scaling, no idle cost  
* Trade-off: Lambda is chosen for burst scalability and cost efficiency. However, it is constrained by execution limits (\~15 minutes), making it unsuitable for long-running or CPU-intensive workloads.

#### **Decision 4: No VPC**

* Why: all managed services  
* Trade-off: A VPC is intentionally avoided since all services are managed and do not require private networking. Introducing a VPC would add unnecessary cost (e.g., NAT Gateway) and operational complexity without meaningful benefit.

#### **Decision 5: DynamoDB**

* Why: fast, scalable state tracking. DynamoDB is used to track job lifecycle (pending, processing, completed, failed), enabling observability and idempotent processing.  
* Trade-off: eventual consistency considerations

#### **Decision 6: Cognito**

* Used for user authentication  
* Used for user authorisation, so each time a request is sent, an auth token is also sent along with it, which allows the backend to securely generate the URLs only for authorised users.  
* Allows Google, Apple, Meta, etc., sign-ups, along with custom ones, allowing flexibility at any scale.

#### **Decision 7: S3**

* We need a resilient storage solution without exceeding the cost limits, so S3 stands as the primary choice for storing the files that are to be processed.  
* We also need a storage that scales irrespective of load, because the solution assumes burst scenarios, the storage is the last thing we want to break in this system, that’s why other options like EBS, Instance store are ruled out.  
* Options like RDS and DocumentDB won’t be a cost-efficient choice here; they also won’t allow the file flexibility like S3, since we’re designing it for a large set of file types.

#### **Decision 8: API & API Gateway**

* Single point access is required here, and the API allows exactly that without exposing the entire Back-End.  
* API Gateway simply allows us to design different types of APIs.

---

### **4\. Failure Handling**

* Retry strategy (mention backoff)  
* **Dead Letter Queue**  
* Idempotency approach  
* Messages are retried using exponential backoff  
* Failed messages are moved to a Dead Letter Queue after threshold retries  
* Processing is idempotent using job IDs to prevent duplicate execution  
* Visibility timeout ensures failed workers do not lose messages

---

### **5\. Cost Thinking (very important)**

* The system is designed so that compute scales with actual workload, while the queue absorbs burst traffic, preventing uncontrolled concurrency and cost spikes.  
* Lambda is used so that the costs of long-running servers aren’t wasted on idle compute costs.  
* S3 events reduce management overhead and allow us to avoid evetbridge events, which introduce extra costs.

Now we’ll try to get a rough cost estimate:  
**Assumptions**   
*1,000 users/day*  
*Each uploads 2 files*  
*Total: 2,000 files/day*  
*Avg processing time: 5 seconds*  
*Lambda memory: 512 MB*  
*Lambda cost (actual math)*

Lambda pricing roughly:  
$0.0000167 per GB-second

**So:**  
0.5 GB × 5 sec \= 2.5 GB-sec per request  
2,000 requests → 5,000 GB-sec/day  
**Cost:**  
5,000 × 0.0000167 ≈ $0.083/day  
Monthly ≈ $2.5  
**S3 cost** **Storage:** assume 50GB → \~$1–2/month  
**Requests:** negligible  
SQS cost  
Millions of requests are pennies  
Practically \~$0.5 or less  
**DynamoDB**  
Small metadata, low R/W  
\~$1–3/month  
**Total realistic cost:**  
\~$5–10/month (\~₹400–₹800)  
This cost scales as the number of requests, which is 2000 per day currently, increases.  
Eg. 200,000 files/day   
**Updated total:** \~$350/month  
---

### **6\. What we are NOT solving (critical maturity signal)**

This system is intentionally scoped to focus on burst ingestion and asynchronous processing. It does not address:

* Real-time or synchronous processing  
* Multi-region redundancy  
* Long-term storage optimization  
* Domain-specific processing logic  
* Advanced authorization models

---

### **7\. Observability**

* Logs: capture processing steps and failures  
* Metrics: queue depth, processing latency  
* Alerts: trigger on DLQ growth or failure spikes
