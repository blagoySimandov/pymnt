# Makefile for PyMNT project
PYTHON := python3

TEST_DIR := ./examples

REQUIREMENTS := requirements.txt
ARGS := ./examples/example.py fibonacci_iterative

install:
	$(PYTHON) -m pip install -r $(REQUIREMENTS)

test:
	$(PYTHON) -m unittest $(TEST_DIR)/example_test.py

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -exec rm -f {} +

run:
	$(PYTHON) -m pymnt $(ARGS)

all: install run



