# BlastHub

### Event-Driven Async File Processing System on AWS

BlastHub is a serverless, event-driven file processing pipeline designed to handle burst uploads using asynchronous queue-based processing on AWS.

The system uses S3, SQS, Lambda, DynamoDB, and API Gateway to decouple upload traffic from processing workloads while supporting retry handling, DLQ-based failure isolation, status tracking, and observability through CloudWatch metrics and structured logging.

---

## Problem Statement

Synchronous file-processing systems can become unreliable during sudden traffic spikes due to tightly coupled upload and processing workflows.

BlastHub was built to explore how asynchronous, queue-based architectures improve workload isolation, failure handling, and scalability in serverless cloud environments.

---

## System Overview

BlastHub accepts file uploads through pre-signed URLs and processes them asynchronously using an event-driven AWS architecture.

The system:
- decouples uploads from processing using SQS
- absorbs burst traffic through queue buffering
- tracks job state in DynamoDB
- isolates failed processing through DLQ handling
- emits CloudWatch metrics for operational visibility

---

## Architecture Diagram


<img width="1243" height="679" alt="image" src="https://github.com/user-attachments/assets/2fabe5f9-f140-402f-94d4-61061e82c0d8" />


---

## System Flow

1. Client requests a pre-signed upload URL through API Gateway
2. Upload Lambda generates:
   - pre-signed S3 upload URL
   - unique job ID
3. Client uploads file directly to S3
4. S3 event notification sends metadata to SQS
5. Processing Lambda consumes messages from SQS
6. Processing metadata and job state are written to DynamoDB
7. CloudWatch metrics and structured logs are emitted during processing
8. Status API retrieves current processing state using job ID
9. Failed processing attempts are retried automatically before routing to DLQ

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

### Dead-Letter Queue
- Failed processings in Queue are routed to DLQ
- Processing failure 3 times in a row pushes the message to DLQ
- Allows retaining of failed processes
- Keeps record of what failed as well

### Serverless Compute
- Auto-scales with demand
- No idle cost

### Database for State Tracking
- Stores job status (success, failed)
- Enables user status queries

### No VPC (Intentional)
- All services are managed
- Avoids unnecessary cost and complexity
- VPC only needed for private resources like databases

---

## Failure Handling

- Failed messages are retried automatically through SQS visibility timeout and Lambda retry behavior
- Messages exceeding maxReceiveCount (currently 3) are routed to a Dead Letter Queue (DLQ)
- FAILED processing states are persisted in DynamoDB
- Structured logging and CloudWatch metrics improve failure visibility and debugging

---

## Cost Considerations

- Serverless architecture avoids idle infrastructure costs
- Pre-signed uploads reduce backend bandwidth and compute overhead
- Queue-based decoupling prevents overprovisioning for burst workloads
- No VPC or NAT Gateway usage to avoid unnecessary networking costs
- Processing infrastructure scales on demand through Lambda concurrency

---

## Security

- Private storage (no public access)
- Pre-signed URLs for secure upload/download
- Least-privilege IAM roles
- Lambda (Serverless Compute) scoped using least-privilege access principles

---

## Failure Scenario

If processing Lambda fails:

1. Message remains unacknowledged
2. SQS visibility timeout expires
3. Message becomes available again
4. Lambda retries processing
5. After maxReceiveCount exceeded, message moves to DLQ
6. FAILED state persisted in DynamoDB

---

## Future Improvements

- Authentication and user-level access control
- Request rate limiting and abuse protection
- Content validation during upload
- Infrastructure-as-Code deployment automation
- Extended monitoring dashboards and alerting

---

## Tech Stack

- Amazon S3
- Amazon SQS
- AWS Lambda
- Amazon DynamoDB
- Amazon API Gateway
- Amazon CloudWatch
- AWS IAM

---

## What This Project Demonstrates

- Event-driven serverless architecture
- Asynchronous workload processing
- Queue-based burst traffic handling
- Distributed failure isolation using DLQs
- DynamoDB-based state tracking
- Cloud-native observability with CloudWatch metrics
- Cost-aware AWS infrastructure design
- Practical experience debugging distributed workflows

-----

## Operational Lessons Learned

- Native S3 event notifications proved simpler and more appropriate than introducing EventBridge for the current workload requirements.
- Initial designs required further decomposition during implementation, leading to dedicated Lambdas for processing and status retrieval to simplify responsibilities and debugging.
- Queue-based decoupling simplified handling of upload bursts by separating ingestion throughput from processing throughput.
- Simulating processing failures helped validate retry behavior and reinforced the importance of DLQ-based failure isolation in asynchronous systems.
- Structured logging significantly improved debugging across asynchronous processing stages and failure scenarios.
- Custom CloudWatch metrics became increasingly valuable once multiple asynchronous components were introduced into the workflow.
- DynamoDB status tracking required careful handling to avoid inconsistent job states during failed processing attempts.
