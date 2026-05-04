# APEX Development Guide

This file is the working guide for agents and engineers editing this checkout.
Keep it aligned with the live repository, not with adjacent APEX-related
projects.

## Project Overview

- APEX is the `apex-flow` Python package for automated alloy property
  workflows. It prepares calculation tasks, dispatches them through dflow or
  local debug paths, retrieves outputs, archives results, and generates reports.
- Package metadata currently lives in `setup.py`: package name `apex-flow`,
  version `1.3.0`, Python `>=3.10`, console entry point
  `apex = apex.__main__:main`, LGPLv3 license.
- The public user flow is configuration-driven. Users provide structure
  directories, one or more `param_*.json` files, and an optional global config
  such as `global_bohrium.json`.
- Supported calculators are LAMMPS-family interactions, VASP, and ABACUS.
  Supported execution backends include local debug mode, dflow/Argo, Bohrium,
  and DPDispatcher contexts such as SSH/HPC or local dispatcher contexts.
- The current checkout has generated/untracked `build/` and
  `apex_flow.egg-info/` directories. Treat them as build artifacts unless the
  user explicitly asks to inspect or commit them.

## Architecture And Code Graph

- CLI entry: `apex/main.py` defines subcommands including `submit`, `do`,
  `retrieve`, `list`, `get`, `getsteps`, `getkeys`, `delete`, `archive`, and
  `report`. `apex/__main__.py` forwards to this CLI.
- Submission path: `apex/submit.py` loads config and parameter JSON, determines
  the workflow type, packs upload directories, configures dflow/Bohrium, builds
  a `FlowGenerator`, submits workflows, monitors completion, retrieves outputs,
  and archives results.
- Workflow graph: `apex/flow.py` owns `FlowGenerator`, which builds dflow
  `Workflow`, `Step`, and `Task` objects. Recent history decomposes relaxation
  and property work per structure, reuses templates to reduce manifest size,
  and supports skip/reuse behavior for finished tasks.
- OP layer: `apex/op/relaxation_ops.py` and `apex/op/property_ops.py` are dflow
  OP wrappers. They bridge artifacts and parameters into core functions,
  perform post-processing, and clean sensitive or bulky potential files from
  retrieved outputs.
- Local step path: `apex/step.py` implements `apex do` for local
  `make_relax`, `run_relax`, `post_relax`, `make_props`, `run_props`, and
  `post_props`. Local post steps attempt non-fatal archive generation for
  parity with `apex submit`.
- Scientific core: `apex/core/common_equi.py` handles relaxation task creation,
  run, and post logic. `apex/core/common_prop.py` dispatches property task
  creation, run, and post logic.
- Property modules: `apex/core/property/` contains the property implementations:
  EOS, Cohesive, Decohesive, Elastic, Surface, Vacancy, Interstitial, Gamma,
  Phonon, Gruneisen, and FiniteTlatt. Add new property types through
  `make_property_instance` and tests.
- Calculator modules: `apex/core/calculator/` contains VASP, ABACUS, LAMMPS,
  task abstractions, and calculator factory logic. Keep calculator-specific
  input/output file rules inside this layer.
- Reporting and archive: `apex/report.py`, `apex/reporter/`, and
  `apex/archive.py` collect results, build reports, and write local or database
  archives. `apex/database/` supports local, MongoDB, and DynamoDB style
  storage paths.

## Supported Workflows And Features

- Workflow types are relaxation-only, property-only, and joint relaxation plus
  property workflows. The CLI can infer them from parameter files or accept an
  explicit `--flow` value.
- Property calculations currently include equation of state, cohesive energy,
  decohesive energy, elastic constants, surface energy, vacancy formation,
  interstitial formation, generalized stacking fault energy, phonon spectra,
  Gruneisen/thermal-expansion workflows, and finite-temperature lattice
  parameters.
- `rerun_finished=False` is an important behavior. Current code skips finished
  relaxation/property results in relaxation, property, and joint workflows when
  required result files are present. Do not break this while changing upload,
  backup, or per-structure scheduling code.
- Joint workflows may reuse existing relaxation outputs and may skip individual
  finished property directories while still running pending structures or
  properties.
- Property `cal_setting.overwrite_interaction` allows property-specific
  calculator settings. Preserve this override in make/run/post paths.
- Mismatched relaxed structures may be skipped when a property has
  `skip_mismatch=True`.

## Configuration And Dependencies

- Runtime dependencies are declared in `setup.py`. Key libraries include
  `numpy<2.0.0`, `pydflow>=1.7.83`, `pymatgen`, `pymatgen-analysis-defects`,
  `dpdata==0.2.17`, `dpdispatcher`, `phonopy`, `plotly`, `dash`,
  `dash_bootstrap_components`, `seekpath`, `fpop`, `boto3`, `pymongo`,
  `scipy`, `matplotlib`, `pandas`, `requests`, `PyYAML`, `dargs`, and
  `packaging`.
- External tools and services are not optional for end-to-end production runs:
  LAMMPS, VASP, ABACUS, phonopy/phonoLAMMPS, Bohrium, dflow/Argo, Docker images,
  SSH/HPC schedulers, and database services may be required depending on config.
- `apex/config.py` maps global JSON into dflow config, s3 config, Bohrium
  credentials, dispatcher config, basic image/run-command settings, and archive
  database settings.
- Example configs may contain credential placeholders. Never commit real
  Bohrium passwords, SSH passwords, cloud tokens, database secrets, or private
  potential files.
- README and examples are user-facing API documentation. If parameter schema,
  workflow behavior, image names, or CLI behavior changes, update examples and
  README in the same change.

## Development Environment

- Use Python 3.10 compatibility as the baseline because CI runs Python 3.10.
  The package declares `python_requires='>=3.10'`.
- The current project packaging source is `setup.py`. There is no root
  `pyproject.toml` in this checkout, so do not assume a uv, Poetry, hatch, or
  setuptools-modern workflow unless one is added.
- Install for local development with `pip install -e .`. Install test
  dependencies with `pip install -e ".[test]"`; this extra is defined in
  `setup.py` for the current CI workflow.
- Keep generated or environment directories out of commits: `.venv/`, `build/`,
  `dist/`, `*.egg-info/`, coverage artifacts, local workflow outputs, retrieved
  simulation outputs, and temporary debug directories.
- Many tests and examples create or remove directories under `tests/` input
  folders. Inspect `git status --short` before and after running them.

## Testing And CI

- GitHub Actions workflow `.github/workflows/main.yml` runs on push and pull
  request with Python 3.10.
- CI install commands are:
  `pip install --upgrade pip` and `pip install -e ".[test]"`.
- CI test command runs from `tests/`:
  `SKIP_UT_WITH_DFLOW=0 DFLOW_DEBUG=1 coverage run -m unittest -v -f`,
  followed by `coverage report`.
- This repository uses `unittest` as the observed test runner. Do not describe
  pytest as the canonical test runner unless the project migrates or adds a
  pytest config.
- For targeted local validation, prefer the smallest relevant unittest module,
  for example `cd tests && python -m unittest -v test_gruneisen`.
- For changes touching dflow OP signatures, workflow generation, or task
  packaging, include tests around artifact paths and generated task lists.
- For changes touching a property class, cover validation, `task_type`,
  `task_param`, generated task directory shape, and `compute`/post behavior
  where feasible.
- For changes touching calculators, cover generated input files, forwarded and
  backward files, and cleanup of potential/model files.

## Git And Collaboration

- Current branch layout observed in this checkout: `exp-1.3.0` points at the
  same commit as local and remote `devel-1.3.0`; `main` tracks `origin/main`.
  Re-check branch state before any commit or push.
- Recent git history emphasizes README updates, Gruneisen workflows, phonon and
  LAMMPS toolchain validation, `rerun_finished=False`, per-structure relaxation
  and property scheduling, finite-temperature lattice parameters, decohesive
  updates, and example maintenance. Preserve these behaviors when refactoring.
- Keep commits scoped. Do not include generated directories, local environments,
  downloaded artifacts, credentials, or unrelated outputs in code/documentation
  commits.
- Before committing, run `git status --short`, inspect `git diff`, and verify
  that only intended files are staged.
- Prefer non-interactive git commands. Do not rewrite history, delete branches,
  or force-push unless explicitly requested.
- If branch synchronization matters, verify with `git branch -vv`,
  `git remote -v`, and, when permitted, `git fetch` plus divergence counts.

## Engineering Risks And Gaps

- Packaging note: test dependencies are centralized under the `test` extra in
  `setup.py`; keep CI and local install commands aligned with it.
- Hygiene note: root `.gitignore` excludes generated packaging, environment,
  cache, coverage, and local workflow artifacts. Do not stage ignored artifacts
  by force unless the user explicitly asks.
- Tooling gap: no lint, formatting, type-checking, tox, or pytest config was
  observed. Add those intentionally rather than assuming defaults.
- Safety gap: external simulation commands still use shell execution in some
  paths. Do not reintroduce shell-based file cleanup for paths derived from user
  config or interaction model names.
- Integration gap: many real workflows depend on heavyweight external
  executables and cloud services. Unit tests should mock external commands where
  possible and separate local deterministic validation from production workflow
  submission.
- Documentation drift risk: README badge is aligned with `1.3.0`; Bohrium image
  tags in examples may still lag the Python package version, so confirm actual
  registry availability before changing image tags.
- Secret-management risk: `global_bohrium.json` examples describe credentials.
  Keep examples placeholder-only and avoid logging secrets.
- Compatibility risk: scientific file formats and third-party libraries change
  often. When upgrading dependencies, run calculator-specific tests and inspect
  generated files, not just import checks.

## Agent Operating Rules

- Read the relevant code path before editing. This project has parallel local,
  dflow, dispatcher, and archive paths that must stay consistent.
- Preserve public JSON parameter keys and output directory conventions unless
  the task explicitly includes a migration.
- Do not run real Bohrium, SSH/HPC, VASP, ABACUS, or long LAMMPS submissions
  unless the user explicitly asks and required credentials/resources are clear.
- Prefer small, targeted tests after edits. Full workflow submission is not a
  substitute for unit coverage around parameter handling and generated files.
- Treat `build/` and `apex_flow.egg-info/` as generated artifacts in this
  checkout. Do not modify or stage them unless the user asks.
- If adding a new property, update the property class, the factory in
  `apex/core/common_prop.py`, examples/README parameter docs, and tests in one
  coherent change.
- If changing workflow graph generation, verify local debug behavior and dflow
  OP behavior separately because they share scientific core code but not the
  same artifact plumbing.
