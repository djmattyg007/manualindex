import os
import sys

from invoke import task, util


in_ci = os.environ.get("CI", "false") == "true"
if in_ci:
    pty = False
else:
    pty = util.isatty(sys.stdout) and util.isatty(sys.stderr)


@task
def reformat(c):
    c.run("isort manualindex tasks.py", pty=pty)
    c.run("black manualindex tasks.py", pty=pty)


@task
def lint(c):
    c.run("flake8 --show-source --statistics manualindex", pty=pty)


@task
def type_check(c):
    c.run("mypy manualindex", pty=pty)
