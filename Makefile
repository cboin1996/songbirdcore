APP_NAME=songbirdcore
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
ENV_VARS = $(shell cat $(ENV).env | xargs)

.PHONY: setup
setup:
	@echo sets up the development environment
	python3 -m venv venv
	@echo activate venv with 'source venv/bin/activate'

.PHONY: requirements
REQUIREMENTS_FILE=requirements.txt
requirements:
	pip install -r $(APP_NAME)/$(REQUIREMENTS_FILE)
	pip install -e .

.PHONY: update-requirements
REQUIREMENTS_FILE=requirements.txt.blank
update-requirements: requirements
	pip freeze --exclude-editable > $(APP_NAME)/requirements.txt

lint:
	black $(APP_NAME)/.

test:
	$(ENV_VARS) python -m pytest test/unit -v