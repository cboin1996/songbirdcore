# songbirdcore 🐦

Low-level package with common code used across songbird's
cli and api.

See: 

- [songbirdcli](https://github.com/cboin1996/songbird.git)
- [songbirdapi](https://github.com/cboin1996/songbirdapi.git)

## Requirements

- Python version >= 3.11
- Clone [my fork of requests-html: requests-htmlc](git@github.com:cboin1996/requests-html.git)

    ```bash
        git clone https://github.com/cboin1996/requests-html.git
        git checkout dev
    ```

## Development

Once you have clone the repository, run

```bash
make setup
source venv/bin/activate
make requirements
```

This configures a virtual environment locally.
You can then run tests by performing the steps below.

## Tests

Configure your vscode debugger by creating a `.vscode/settings.json`
file with the following contents:

```json
{
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true,
}
```