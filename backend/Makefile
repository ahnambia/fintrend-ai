.PHONY: help install fmt lint type test

help:
\t@echo "install, fmt, lint, type, test"

install:
\tpython -m pip install -U pip
\tpip install -e . || true
\tpip install black ruff mypy pytest

fmt:
\tblack .
\truff --fix .

lint:
\truff .

type:
\tmypy .

test:
\tpytest -q
