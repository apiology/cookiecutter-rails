"""Run the cookiecutter template and verify it succeeds."""

from contextlib import contextmanager
import datetime
import os
import shlex
import subprocess
import sys

from cookiecutter.utils import rmtree
import jinja2


@contextmanager
def inside_dir(dirpath):
    """Execute code from inside the given directory.

    :param dirpath: String, path of the directory the command is being run.
    """
    old_path = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


@contextmanager
def suppressed_github_and_circleci_creation():
    """Avoid external mutations while running tests."""
    os.environ['SKIP_EXTERNAL'] = '1'
    try:
        yield
    finally:
        del os.environ['SKIP_EXTERNAL']


def errmsg(exception):
    """Create error message from exception."""
    if isinstance(exception, jinja2.exceptions.TemplateSyntaxError):
        return f'Found error at {exception.filename}:{exception.lineno}'
    return str(exception)


@contextmanager
def bake_in_temp_dir(cookies, *args, **kwargs):
    """Delete the temporal directory that is created when executing the tests.

    :param cookies: pytest_cookies.Cookies,
        cookie to be baked and its temporal files will be removed
    """
    with suppressed_github_and_circleci_creation():
        result = cookies.bake(*args, **kwargs)
        assert result is not None, result
        assert result.exception is None, errmsg(result.exception)
        assert result.exit_code == 0
        assert hasattr(result, 'project_path'), result
    try:
        yield result
    finally:
        rmtree(str(result.project_path))


def run_inside_dir(command, dirpath):
    """Run a command from inside a given directory, returning the exit status.

    :param command: Command that will be executed
    :param dirpath: String, path of the directory the command is being run.
    """
    with inside_dir(dirpath):
        return subprocess.check_call(shlex.split(command))


def check_output_inside_dir(command, dirpath):
    """Run a command from inside a given directory, returning the command output."""
    with inside_dir(dirpath):
        return subprocess.check_output(shlex.split(command))


def project_info(result):
    """Get toplevel dir, project_slug, and project dir from baked cookies."""
    project_path = str(result.project_path)
    project_slug = os.path.split(project_path)[-1]
    project_dir = os.path.join(project_path, project_slug)
    return project_path, project_slug, project_dir


def test_bake_and_run_build(cookies):
    """Run the template and verify it succeeds."""
    with bake_in_temp_dir(cookies,
                          extra_context={
                              'full_name': 'name "quote" O\'connor',
                              'project_short_description':
                              'The greatest project ever created by name "quote" O\'connor.',
                          }) as result:
        assert result.project_path.is_dir()
        assert result.exit_code == 0
        assert result.exception is None

        found_toplevel_files = [f.name for f in result.project_path.iterdir()]
        assert 'README.md' in found_toplevel_files
        assert 'LICENSE' in found_toplevel_files
        assert 'fix.sh' in found_toplevel_files

        assert run_inside_dir('make test', str(result.project_path)) == 0
        assert run_inside_dir('make typecheck', str(result.project_path)) == 0
        assert run_inside_dir('make quality', str(result.project_path)) == 0
        # The supplied Makefile does not support win32
        if sys.platform != 'win32':
            output = check_output_inside_dir(
                'make help',
                str(result.project_path)
            )
            assert b'run precommit quality checks' in \
                output
        license_file_path = result.project_path / 'LICENSE'
        circle_ci_config = result.project_path / '.circleci' / 'config.yml'
        # ensure no unresolved ninja comments remain in .yml file
        assert 'cookiecutter.' not in circle_ci_config.open().read()
        now = datetime.datetime.now()
        assert str(now.year) in license_file_path.open().read()
        print('path:', str(result.project_path))


def test_bake_and_run_build_non_default_options(cookies):
    """Run the template with non-default options and verify it succeeds."""
    with bake_in_temp_dir(cookies,
                          extra_context={
                              'api_only': 'Yes',
                              'use_checkoff': 'Yes',
                          }) as result:
        assert result.project_path.is_dir()
        assert result.exit_code == 0
        assert result.exception is None

        assert run_inside_dir('make test', str(result.project_path)) == 0
        assert run_inside_dir('make typecheck', str(result.project_path)) == 0
        assert run_inside_dir('make quality', str(result.project_path)) == 0
        print('path:', str(result.project_path))
