# Contributing to Kurigram

Thanks for taking the time to contribute! This document covers how to set up a development
environment, the expected workflow, and what we look for in a pull request.

## Getting started

Kurigram requires Python `>=3.8`.

```bash
make venv-dev
```

This creates `venv/` and installs the package together with its development dependencies.
Every `make` recipe below runs against that interpreter, so create it first.

### Generated code

`pyrogram/raw/{types,functions,base,all.py}` and `pyrogram/errors/exceptions/` are generated from
TL schema files and are not tracked in git. Run the generator before working on anything that
touches type checking or code that imports from `pyrogram.raw`, and again after any change
under `compiler/api/source`:

```bash
make api
```

Never hand-edit files under these paths. If a change appears to require editing generated code,
the actual fix belongs in the compiler/templates under `compiler/`, or in the code that consumes
the generated types.

## Development workflow

Run these before opening a pull request:

```bash
make lint          # ruff check
make typecheck     # ty check (requires `make api` to have been run first)
make test-unit     # the offline suite, no relay or session needed
```

`make test` runs the full suite, including the integration tests. Those open real sockets and
take every endpoint from a git-ignored `.env.test` file: a live MTProto or web proxy relay and a
prepared session, listed in `.env.test.example`. Each one skips by name when its variable is
absent, so a checkout without that file still runs the whole offline suite.

A test's directory decides its marker, so put it in the tree that matches what it needs:
`tests/integrations/` when it opens a socket or talks to a real service, `tests/unit/`
otherwise. A test outside both is not collected as unmarked, it fails the run:

```
ERROR: test_example.py is outside tests/unit and tests/integrations - every test lives in one of the two.
```

### Optional: pre-commit hook

The repository ships a `pre-commit` config that runs `make lint` and `make typecheck` on commit,
the same two checks CI runs, so a breach never reaches review:

```bash
pre-commit install
```

### Linting and type checking policy

`ruff`'s selected rule set and `ty`'s rule overrides in `pyproject.toml` are both intentionally
narrower than "everything the tool can check": they're expanded incrementally, one rule at a
time, as the codebase is brought into compliance with it. When contributing:

- Don't widen an ignored `ty` rule or narrow the `ruff` rule set just to make a change pass.
- Fix the underlying issue instead.
- Don't make unrelated style changes to code outside the rules already enforced; keep pull
  requests focused on their stated purpose.

## Code style conventions

A few conventions that have come up repeatedly in code review but aren't enforced by `ruff` or
`ty`, so they're written down here instead:

- **Every new `.py` file carries the licence header** that the rest of the tree carries: copy it
  from a module in the same package. The only files without one are the empty package
  `__init__.py` files. Nothing checks this, so a missing header only surfaces in review.
- **Annotations are evaluated at runtime and the floor is Python `3.8`.** Nothing in the tree uses
  `from __future__ import annotations`, and CI runs the suite on every version from `3.8` up, so
  `list[str]` and `int | None` in a signature pass on a modern interpreter and fail the matrix
  with `TypeError: 'type' object is not subscriptable` and `TypeError: unsupported operand
  type(s) for |: 'type' and 'NoneType'`. Use `List[str]` and `Optional[int]` from `typing`.
- **No `assert` for runtime guards in library code.** `assert` statements are stripped when
  Python runs with `-O`, and raise a bare `AssertionError` with no context for library consumers.
  Raise `RuntimeError` (or a more specific exception) instead.
- **When raising with a message, assign it to a variable first**, then raise it, rather than
  writing the message inline in the `raise` statement:

  ```python
  msg = f"connection not open (state={self._state})"
  raise RuntimeError(msg)
  ```

- **All code references in comments use backticks**, and every reference in the comment, not
  just the first one. Write ``Call `Client.stop()` before `Client.start()`.``, not
  `Call Client.stop() before Client.start().`
- **No em dashes or `--` as punctuation in comments.** Use a comma, colon, parentheses, or a
  single `-` instead.
- **Every `# ty: ignore[rule]` carries a reason** after a single `-`, as in
  `# ty: ignore[unresolved-import] - optional, not a project dependency`. Only the `[rule]`
  bracket is `ty`'s own syntax; the reason is ours, so nobody has to reconstruct why the
  ignore is there.
- **A parameter that needs to distinguish "not passed" from a meaningful `None`** (for example,
  a `reply_markup` parameter where `None` means "remove the markup") should default to the
  `object` class itself (not an instance of it) as the "not specified" sentinel, keeping `None`
  free to carry its own meaning. Check for existing uses of this pattern elsewhere in the method
  or type before introducing a new one.
- **Test doubles that stand in for `Client`** are named `FakeClient`, not `Client` or `TestClient`
  (pytest warns about `Test*` classes that define `__init__`). Most of the test suite already
  does this: reuse the name rather than inventing one per test file.
- **Module-level constants that never change** should be annotated `Final`.
- **An optional third-party import** (a package the project doesn't depend on, used defensively
  behind a feature that needs it) is marked `# ty: ignore[unresolved-import]`, with the reason
  saying it's optional and linking to the [docs](https://docs.kurigram.icu) section covering
  that feature, if there is one.

## Commit and pull request guidelines

- Write commit messages using [Conventional Commits](https://www.conventionalcommits.org/),
  matching the existing git history: `fix(session): ...`, `feat(deps): ...`, `docs(api): ...`.
  Name a scope; almost every commit on `dev` carries one, and the few that don't are the ones
  nobody can place afterwards.
- **The pull request title matters, not just commit messages.** The project squash-merges, so
  the PR title becomes the actual commit message on `dev`. Title it the same way you would a
  commit: `type(scope): description`, describing what the change actually does rather than a
  generic label. If the branch gains more commits or changes scope before merge, update the title
  to match; don't leave it describing an earlier, narrower version of the change.
- Keep pull requests focused on one logical change. Unrelated fixes should be separate PRs.
- Reference any related issue in the pull request description.

### Before submitting, make sure that

- [ ] `make lint` passes
- [ ] `make typecheck` passes (after `make api`)
- [ ] `make test-unit` passes
- [ ] Tests were added or updated for behavioral changes
- [ ] The commit message(s) follow Conventional Commits

## Questions

If something is unclear, reach out on the [official chat](https://t.me/kurigram_chat) or follow
news and announcements on the [official channel](https://t.me/kurigram_news).
