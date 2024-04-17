APP_NAME=songbirdcore
REQUIREMENTS_FILE=requirements.txt
.PHONY: env
env:
# check ENV env var has been set
ifndef ENV
	$(error Must set ENV variable!)
endif
# load env vars from .env file if present
ifneq ("$(wildcard $(ENV).env)", "")
	@echo "Loading configuration from $(ENV).env"
# include cannot be indented
include $(ENV).env
else
	@echo "Continuing without .env file."
	@echo "Creating template $(ENV).env file"
endif

# variables as a list, required for pytest targets
# in this makefile

.PHONY: setup
setup: env
	@echo sets up the development environment
	python3 -m venv venv
	@echo activate venv with 'source venv/bin/activate'

.PHONY: requirements
requirements: env
	pip install -r $(APP_NAME)/$(REQUIREMENTS_FILE)
# only install dependencies locally if in dev env
ifeq ($(ENV), dev)
	echo "install dev dependencies"
	pip install -e .[dev]
	pip uninstall requests-htmlc
	pip install -e ../requests-html
else
	pip install -e .
endif
	playwright install

.PHONY: update-requirements
update-requirements: env
	pip uninstall requests-htmlc
	pip freeze --exclude-editable | xargs pip uninstall -y
	rm $(APP_NAME)/$(REQUIREMENTS_FILE) || true
	pip install -r $(APP_NAME)/requirements.txt.blank
	pip freeze --exclude-editable > $(APP_NAME)/$(REQUIREMENTS_FILE)

# documentation targets
.PHONY: docs-lint
docs-lint:
	@echo linting files at docs/**/*.md
	markdownlint docs/**/*.md

.PHONY: docs-serve
docs-serve:
	@echo serving the site on http://localhost:8000
	mkdocs serve

.PHONY: docs-build
docs-build:
	@echo building the site
	mkdocs build --strict --verbose --site-dir public

lint:
	black $(APP_NAME)/.
	black tests

test:
	python -m pytest --doctest-modules --junitxml=junit/test-results.xml --cov=songbirdcore --cov-report=xml --cov-report=html tests/unit -v