CMD:=poetry run
PYMODULE:=chinook
TESTS:=tests
PYTEST_FLAGS:=-vv
EXTRACODE:=tick_service.py

.PHONY: all
all: type test lint

.PHONY: clean
clean:
	git clean -Xdf # Delete all files in .gitignore

.PHONY: lint
lint:
	$(CMD) flake8 $(PYMODULE) $(TESTS) $(EXTRACODE)

.PHONY: type
type:
	$(CMD) mypy $(PYMODULE) $(TESTS) $(EXTRACODE)

.PHONY: test
test:
	$(CMD) pytest $(PYTEST_FLAGS) --cov=$(PYMODULE) $(TESTS)

.PHONY: test-cov
test-cov:
	$(CMD) pytest $(PYTEST_FLAGS) --cov=$(PYMODULE) $(TESTS) --cov-report html

.PHONY: isort
isort:
	$(CMD) isort $(PYMODULE) $(TESTS) $(EXTRACODE)
