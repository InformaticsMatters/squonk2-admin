# Developer README

## Contributing
The project uses: -

- [pre-commit] to enforce linting of files prior to committing them to the
  upstream repository
- [Commitizen] to enforce a [Conventional Commit] commit message format
- [Black] as a code formatter

You **MUST** comply with these choices in order to  contribute to the project.

To get started review the pre-commit utility and the conventional commit style
and then setup your local clone by following the **Installation** and
**Quick Start** sections: -

    pip install --upgrade pip
    pip install -r build-requirements.txt
    pre-commit install -t commit-msg -t pre-commit

Now the project's rules will run on every commit, and you can check the
current health of your clone with: -

    pre-commit run --all-files

Create a virtual environment if you're going to develop code.

## Building
It's a standard Python package, controlled by `setup.py` so familiarity
with [Python packaging] will help. The project is built and published
to PyPI automatically from the main branch using GitHub Actions.

To build the package distribution manually run: -

    python -m pip install --upgrade build
    rm -rf dist/*
    python -m build --sdist --wheel --outdir dist/

>   Because you're building outside the CI process the version number of
    the package will be fixed at 1.0.0. DO NOT change this behaviour.

To install the local build, without needing to publish the package run: -

    pip install dist/im-squad-*.tar.gz

And to uninstall...

    pip uninstall im-squad -y

## Testing
We use [coverage] and [pytest] to test the project.
You can run the unit tests with: -

    PYTHONPATH=./src coverage run -m pytest -m unit --strict-markers
    coverage report -m

> If you've installed **SquAd** you will need to uninstall it
  with `pip uninstall im-squad -y` before running any tests.

---

[black]: https://black.readthedocs.io/en/stable
[commitizen]: https://commitizen-tools.github.io/commitizen/
[conventional commit]: https://www.conventionalcommits.org/en/v1.0.0/
[pre-commit]: https://pre-commit.com
[pytest]: https://docs.pytest.org/en/7.1.x/contents.html
[python packaging]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
