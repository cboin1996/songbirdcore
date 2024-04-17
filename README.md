# songbirdcore 🐦

Low-level package with common code used across songbird's
cli and api.

See: 

- [songbirdcli](https://github.com/cboin1996/songbird.git)
- [songbirdapi](https://github.com/cboin1996/songbirdapi.git)

## Documentation

`songbirdcore`'s documentation may be found [here](https://cboin1996.github.io/songbirdcore)

## Requirements

- Python version >= 3.11

## Installation

To install, run

```bash
pip install songbirdcore
```

To install the latest development version from `test-pypi`
run

```bash
    python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ songbirdcore
```

## Development

Once you have clone the repository, run

```bash
export ENV=dev
make setup
source venv/bin/activate
make requirements
```

This configures a virtual environment locally.
You can then run tests by performing the steps below.

### Updating Requirements

Updating the requirements for this package may be done
through

```bash
make update-requirements
make requirements
```

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