"""Nox tasks for code quality assessment."""
import nox
from nox.sessions import Session

nox.options.sessions = ["tests", "lint", "mypy"]
locations = ("src", "tests", "noxfile.py")


@nox.session(python=["3.11"])
def tests(session: Session) -> None:
    """Run tests."""
    args = session.posargs or ["--cov", "--doctest-modules"]
    session.run("poetry", "install", external=True)
    session.run("pytest", *args)


@nox.session(python=["3.11"])
def lint(session: Session) -> None:
    """Check style problems."""
    args = session.posargs or locations
    session.install("wemake-python-styleguide")
    session.run("flake8", *args)


@nox.session(python=["3.11"])
def mypy(session: Session) -> None:
    """Check types consistency."""
    args = session.posargs or locations
    session.run("poetry", "install", external=True)
    session.run("mypy", *args)


@nox.session(python="3.11")
def coverage(session: Session) -> None:
    """Upload coverage data."""
    session.install("coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)
