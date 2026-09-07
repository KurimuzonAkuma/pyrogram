# `uv` owns the environment. `uv run` creates `.venv` and installs from `uv.lock` whenever
#  it is missing or out of date, so no recipe below has to build one first and there is no
#  step a contributor can forget.
UV := uv
PYTHON := $(UV) run python

# The live tests take every parameter from the environment. `.env.test` is the
#  git-ignored file that carries them locally; the runner loads it so nothing
#  under `tests/` has to read a file of its own. Absent, the tests skip by name.
ENV_TEST := .env.test
LOAD_ENV_TEST := set -a; if [ -f $(ENV_TEST) ]; then . ./$(ENV_TEST); fi; set +a;
# `hatchling` reads `[tool.hatch.version]`, so this is the number the build backend
#  stamps on the artifacts. `--no-project --with` keeps it to one ephemeral package,
#  because the release jobs read the version without syncing the project.
VERSION = $(shell $(UV) run --no-project --with hatchling hatchling version)
TAG = v$(VERSION)

RM := rm -rf

GREEN  := \033[0;32m
RED    := \033[0;31m
YELLOW := \033[0;33m
BLUE   := \033[0;34m
BOLD   := \033[1m
RESET  := \033[0m

.PHONY: sync version clean-venv clean-build clean-api clean-docs clean api docs docs-archive build tag dtag lint typecheck test test-unit test-guards test-integration

# No other recipe needs this: they all sync on their own. It exists so CI can install in
#  a step of its own, which is what makes a resolution failure read as one in the log
#  instead of as whatever recipe happened to run first.
sync:
	$(UV) sync
	@printf "$(YELLOW)Synced .venv with %s$(RESET)\n" "$$($(PYTHON) --version)"

clean-venv:
	$(RM) .venv
	@printf "$(YELLOW)Cleaned venv directory$(RESET)\n"

clean-build:
	$(RM) *.egg-info build dist
	@printf "$(YELLOW)Cleaned build directory$(RESET)\n"

clean-api:
	$(RM) pyrogram/errors/exceptions pyrogram/raw/all.py pyrogram/raw/base pyrogram/raw/functions pyrogram/raw/types
	@printf "$(YELLOW)Cleaned api directory$(RESET)\n"

clean-docs:
	$(RM) docs/build docs/source/api/bound-methods docs/source/api/methods docs/source/api/types docs/source/api/enums docs/source/telegram
	@printf "$(YELLOW)Cleaned docs directory$(RESET)\n"

clean: clean-venv clean-build clean-api clean-docs
	@printf "$(GREEN)Cleaned all directories$(RESET)\n"

api:
	cd compiler/api && $(PYTHON) compiler.py
	cd compiler/errors && $(PYTHON) compiler.py

docs:
	cd compiler/docs && $(PYTHON) compiler.py
	$(UV) run --group docs sphinx-build -b dirhtml "docs/source" "docs/build/html" -j auto

docs-archive:
	cd docs/build/html && zip -r ../docs.zip ./

# `ruff` takes its rule set and its excludes from `pyproject.toml`, so the `lint` job and
#  the `pre-commit` hook both run this recipe instead of spelling the check out again.
lint:
	$(UV) run ruff check

# The rule set and the excludes live in `pyproject.toml`, same as `lint`. Unlike `lint`,
#  this needs `pyrogram.raw.*` to resolve, so `make api` has to have been run first.
typecheck:
	$(UV) run ty check

test:
	@$(LOAD_ENV_TEST) $(PYTHON) -m pytest

test-unit:
	$(PYTHON) -m pytest -m 'not integration'

# `test-unit` selects everything that is not integration, so it runs these too. This
#  target is for working on the guards alone; the two are not disjoint.
test-guards:
	$(PYTHON) -m pytest -m guard

test-integration:
	@$(LOAD_ENV_TEST) $(PYTHON) -m pytest -m integration

build:
	$(UV) build

# The single place that answers "what version is this", for the release jobs as well.
version:
	@printf '%s\n' "$(VERSION)"

tag:
	git tag $(TAG)
	git push origin $(TAG)

dtag:
	git tag -d $(TAG)
	git push origin -d $(TAG)
