SHELL := /bin/bash

.PHONY: help install-dev build pyinstaller dist release

help:
	@echo "Makefile targets:"
	@echo "  make install-dev   # install build tools"
	@echo "  make build         # build sdist and wheel into dist/"
	@echo "  make pyinstaller   # build a single-file executable into dist/pyinstaller/"
	@echo "  make dist          # build both wheel/sdist and pyinstaller binary"
	@echo "  make release       # run ./release.sh to publish a GitHub release (requires gh CLI)"

install-dev:
	python -m pip install --upgrade pip build pyinstaller

build:
	python -m pip install --upgrade pip build
	python -m build

pyinstaller:
	python -m pip install --upgrade pyinstaller
	mkdir -p dist/pyinstaller
	pyinstaller --onefile --name file-organizer --distpath dist/pyinstaller organizer/cli.py

dist: build pyinstaller

release: dist
	./release.sh
