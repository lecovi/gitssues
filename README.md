# gitssues

Jira and Github sync issues

![gitssues-flow](docs/img/gitssues-flow.png)

# CLI

You can use CLI to test `gitssues`:

1. Clone the repository
2. Install dependencies with `poetry install`
3. First you need to configure your credentials. 
    1. Create a copy from `env.dist` and name it `.env` in your home directory.
    2. Fill the `.env` file with your credentials. Check [docs](docs/README.md) for more details.
4. Run `poetry run python -m gitssues.cli prepare` to prepare with Jira and Github.

## Cleanup

1. Run `poetry run python -m gitssues.cli clean` to erase cache from Jira and Github.

## API

- `poetry run python -m gitssues.cli jira`: Run Jira actions
    - `poetry run python -m gitssues.cli jira bug`: Run bug commands like `assign`, `comment`, `delete`, `new`, and `transition`.
        - `poetry run python -m gitssues.cli jira bug --help`: For more details
- `poetry run python -m gitssues.cli github`: Run Github actions
    - `poetry run python -m gitssues.cli github issue`: Run issue commands like `close`, `comment`, `new`, and `reopen`.
        - `poetry run python -m gitssues.cli github issue --help`: For more details

## Detailed Jira Flow

- [docs](docs/README.md)

## Detailed Github Flow

- GitHub flow is more straightforward. Hit the correct endpoint and you're done.

# TODO

- [ ] Create Webhook for Jira when comment on an issue
- [ ] Create Webhook for Jira when issue is updated
- [ ] Create Webhook for Jira when transition is applied to an issue
- [x] Create GitHub integration
- [ ] Create GitHub Webhook
- [ ] Create Server endpoints for Jira and GitHub

### Jira Docs

- [Jira Cloud platform Developer
](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/)
- [Jira Software Cloud Developer
](https://developer.atlassian.com/cloud/jira/software/rest/intro/)
