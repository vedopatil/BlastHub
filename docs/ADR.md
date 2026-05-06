#### This is the Architecture Decision Registry created and updated after starting the actual architecture build.

### Tagging Strategy:
* We tag compulsorily with the name "BlastHub"
  * Name = BlastHub, a common tag.
* Environment: Development
    * env = dev
 
### Cost Safety Net
* Since this is an experimental project, we will be keeping any cost spike strictly budgeted and controlled
* For this particular dev env, we will be putting a budget cap of 100 rupees, roughly 1.1 USD
* We'll do this using AWS Budget, as they allow users to create a sophisticated budget with alarms, as needed.
* For the Budget Scope, we'll keep the option of Unblended costs selected to keep a direct track of what spending
    * The budget will also be set to map across all AWS Services, instead of a specified set of filters.

### Region
* We will be making this project in Mumbai (ap-south-1) AWS Region
* This keeps all the services in the same region and complies with data laws since files stored in S3 in the ap-south-1 region won't leave the boundary of the country

### Governance
* We will be making a separate OU or Organisational Unit for this project
* The OU will have sub-units for further management
* For initial phases, there will only be a Dev Sub-OU for the development environment.

### Identity Management
* A separate IAM User, with PowerUserAccess AWS managed job function policy, is attached to the User
* This policy allows the user to access the required Lambda, S3, DynamoDB, API Gateway, and Cognito, which are crucial for this project's architecture
* We will be attaching a new IAM role to the Lambda, which will allow the Lambda to generate Pre-Signed Tokens of S3, for users to upload objects to the bucket directly.


### Pre-Signed URLs
* Used pre-signed URLs to avoid backend load
* Lambda is used to generate Pre-signed URLs
* Lambda has a role that allows access only to the required folder, following the least privilege principle

### The Burst handling using decoupling
* Used SQS to decouple ingestion from processing
* This allows the processing to be queued and decoupled, so failure of any single file will ot affect other file rocessing.
* Since the files are queued, the burst upload of files doesn't break the system since it is queued.
* Dead-Letter Queue or DLQ is used, so if processing fails multiple times, the DLQ handles the failed file processing and allows further integration to notify and resolve the issue.

### Folder simulation in S3 Bucket
* Used prefix-based routing (uploads/raw/)
* Instead of directly uploading to the S3 bucket, the user will upload the files only to a specific folder, uploads/raw/
* This keeps the data logically separate, and allows utilisation of the same S3 bucket for several other future storage needs

### Observability
- CloudWatch logs allow every action to be logged, including API calls to every Lambda action
- Custom Metric was added, named BlastHub, to improve observability
- In the custom metric, both cases, Success and Failure of processing Lambda, are sent to CloudWatch

### Lambda
- Three different Lambda Functions, with three different IAM Roles, are used in this project
- All three roles have least privilege permissions, only allowing what is required for the specific task
- Three places where lambda functions were used are as follows:
   - To generate Pre-signed URLs, sits between API -> [LambdaForUploads] -> S3
   - To process the uploaded files, and store details in DB, sits between S3 -> [ProcessUploadLambda] -> DynamoDB
   - To allow users to check the status of uploaded files, reading from DB, sits between DynamoDB -> [StatusLambda] -> API

### Known gaps
- No auth
- No validation
- No observability beyond logs (a single custom metric implemented)
