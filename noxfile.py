import nox

locations = "src", "tests"
supported_python_versions = ["3.11", "3.10", "3.9", "3.8"]
default_python_version = "3.10"

nox.options.sessions = ["lint", "test"]
nox.options.stop_on_first_error = True


@nox.session(python=supported_python_versions)
def lint(session: nox.Session):
    args = session.posargs or locations
    session.install("flake8")
    session.run("flake8", *args)


@nox.session(python=supported_python_versions)
def test(session: nox.Session):
    session.install("pytest")
    session.install("pytest-cov")
    session.install(".")

    session.env.update({"PY_IGNORE_IMPORTMISMATCH": "1"})

    args = session.posargs or []
    session.run("pytest", *args)


# wrapper for `nox -s test -p 3.10 -- --log-cli-level=LVL`
@nox.session(python=[default_python_version], reuse_venv=True)
def test_logging(session: nox.Session):
    """Wrapper around test session with live logging enabled.

    Usage:
        $ nox -s test_logging
        # set custom log level
        $ nox -s test_logging -- INFO
    """
    lvl = "DEBUG"
    if session.posargs and session.posargs[0] in ["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"]:
        lvl = session.posargs.pop(0)
    session.run(
        "nox", "-r", "-s", "test", "-p", session.python, "--", f"--log-cli-level={lvl}", *session.posargs, external=True
    )
