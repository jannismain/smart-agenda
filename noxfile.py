import nox

locations = "src", "tests"
python_versions = ["3.11", "3.10", "3.9", "3.8"]


@nox.session(python=python_versions)
def lint(session: nox.Session):
    args = session.posargs or locations
    session.install("flake8")
    session.run("flake8", *args)


@nox.session(python=python_versions)
def test(session: nox.Session):
    session.install("pytest")
    session.install("pytest-cov")
    session.install(".")

    session.env.update({"PY_IGNORE_IMPORTMISMATCH": "1"})

    args = session.posargs or []
    session.run("pytest", *args)
