# galadriel

A simple, straight-to-the-point Test Management System, inspired by TestLink and other existing tools.

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=leandrorojas_galadriel&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=leandrorojas_galadriel)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/leandrorojas/galadriel)

Built with [Reflex](https://reflex.dev).

## Getting Started

### Prerequisites

- Python 3.10+

### Installation

1. Clone the repo and check out the latest release:
    ```bash
    git clone https://github.com/leandrorojas/galadriel.git
    cd galadriel
    git fetch --tags
    latestTag=$(git describe --tags "$(git rev-list --tags --max-count=1)")
    git checkout $latestTag
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv .venv/
    source .venv/bin/activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Copy `galadriel.yaml.template` into `galadriel.yaml` and configure it (see [Configuration](#configuration)).

5. Initialize and run:
    ```bash
    reflex db init
    reflex run
    ```

## Configuration

### Site URL

Set `site_url` under the `galadriel` section in `galadriel.yaml` to the URL where the app is hosted. This is used when creating Jira issues to link back to the iteration page. Defaults to `http://localhost:3000` if not set.

```yaml
galadriel:
  site_url: https://your-galadriel-instance.com
```

### Jira Integration

1. Get a Jira API token by following the official Atlassian documentation: [Manage API tokens for your Atlassian account](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).

2. Fill in `galadriel.yaml` with your Jira settings:

    | Key | Description | Example |
    |-----|-------------|---------|
    | `url` | Jira instance URL | `https://instance.atlassian.net` |
    | `user` | Jira username | `yourmail@server.com` |
    | `token` | API token from step 1 | |
    | `project` | Project key for created issues | `TEST` |
    | `issue_type` | Issue type to create | `Bug` |
    | `done_status` | Status considered as Done | `Done` |

    > **Note:** galadriel does not validate Jira object existence yet.

## Contributing

Feel free to turn galadriel into the perfect community product. The request is that you commit your changes to this repo for everyone to enjoy them.

If you want to contribute, galadriel currently needs:
- Additional test coverage
- UI/UX improvements

## License

This project is licensed under the GPL-3.0 License. See [LICENSE](LICENSE) for details.
