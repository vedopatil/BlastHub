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


### Some Key Decisions (Unmentioned earlier)
* Used pre-signed URLs to avoid backend load
* Used SQS to decouple ingestion from processing
* Used prefix-based routing (uploads/raw/)
