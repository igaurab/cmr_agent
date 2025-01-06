APP_DIR=src
APP_FILE=app.py
VENV_DIR=venv
PYTHON=$(VENV_DIR)/bin/python
PIP=$(VENV_DIR)/bin/pip
STREAMLIT=$(VENV_DIR)/bin/streamlit
REQUIREMENTS_FILE=requirements.txt

.DEFAULT_GOAL := run

$(VENV_DIR):
	python3 -m venv $(VENV_DIR)

.PHONY: install
install: $(VENV_DIR)
	$(PIP) install --upgrade pip
	@if [ -f "$(REQUIREMENTS_FILE)" ]; then \
		$(PIP) install -r $(REQUIREMENTS_FILE); \
	else \
		echo "No requirements.txt found."; \
	fi

.PHONY: run
run: $(VENV_DIR)
	cd $(APP_DIR) && ../$(STREAMLIT) run $(APP_FILE)

.PHONY: clean
clean:
	rm -rf $(VENV_DIR)

.PHONY: freeze
freeze: $(VENV_DIR)
	$(PIP) freeze > $(REQUIREMENTS_FILE)
