# Create API Token @ JIRA

Go to your profile security settings https://id.atlassian.com/manage-profile/security/api-tokens
and create an API token.

# Create API Token @ OpsGenie

Go to your integrations page https://nasdaq-meli.app.opsgenie.com/settings/integration/add/API/
and add a new API token.

# Creating a new Bug in Jira

1. Configure Jira Object:
    1. Get **Board** info from *Project Key*
    2. Get **Project** info using *Project Key* from config and *Board ID* from before 
    3. Get **Issue Type** info from *Project Key*
2. Posting a New Bug:
    1. Get **Active Sprint** from *Board*
    2. Post **Issue** to *Project* backlog
    3. Move **Issue** to *Active Sprint*
    4. Assign **Issue** to *User*

# Posting a comment to a Bug in Jira

1. Post **Comment** to Issue using *Issue Key*. [docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-post)

# Change status of a Bug in Jira

1. Get **Issue** Transitions using *Issue Key*. [docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-transitions-get)
2. Change **Issue** Status using *Issue Key* and *Transition ID*. [docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-transitions-post)