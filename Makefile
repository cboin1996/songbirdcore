APP_NAME=songbirdcore

.PHONY: setup
setup:
	uv sync --extra dev
	uv run playwright install

.PHONY: upgrade
upgrade:
	uv lock --upgrade
	uv sync --extra dev

.PHONY: lint
lint:
	uv run black $(APP_NAME)/.
	uv run black tests

.PHONY: test
test:
	uv run pytest --doctest-modules --junitxml=junit/test-results.xml --cov=$(APP_NAME) --cov-report=xml --cov-report=html tests/unit -v

.PHONY: test-stdout
test-stdout:
	uv run pytest --cov=$(APP_NAME) tests/unit -v

.PHONY: docs-lint
docs-lint:
	markdownlint docs/**/*.md

.PHONY: docs-serve
docs-serve:
	mkdocs serve

.PHONY: docs-build
docs-build:
	mkdocs build --strict --verbose --site-dir public
