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
* This keeps all the services in the same region and complies with data laws since files stored in S3 in the ap-south-1 region won't be leaving the boundary of country
