#!/usr/bin/env python

import os
import subprocess

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def remove_file(filepath):
    os.remove(os.path.join(PROJECT_DIRECTORY, filepath))


if __name__ == '__main__':
    if 'Not open source' == '{{ cookiecutter.open_source_license }}':
        remove_file('LICENSE')
        remove_file('CONTRIBUTING.rst')

    subprocess.check_call('./fix.sh')
    if os.environ.get('IN_COOKIECUTTER_PROJECT_UPGRADER', '0') == '1':
        os.environ['SKIP_GIT_CREATION'] = '1'
        os.environ['SKIP_GITHUB_OP_AND_CIRCLECI_CREATION'] = '1'

    if os.environ.get('SKIP_GIT_CREATION', '0') != '1':
        # Don't run these non-idempotent things when in
        # cookiecutter_project_upgrader, which will run this hook
        # multiple times over its lifetime.
        subprocess.check_call(['git', 'init'])
        subprocess.check_call(['git', 'add', '-A'])
        subprocess.check_call(['bundle', 'exec', 'overcommit', '--install'])
        subprocess.check_call(['bundle', 'exec', 'overcommit', '--sign'])
        subprocess.check_call(['bundle', 'exec', 'overcommit', '--sign', 'pre-commit'])
        subprocess.check_call(['make', 'bundle_install'])
        subprocess.check_call(['bundle', 'exec', 'rubocop', '-A'])
        subprocess.check_call(['git', 'add', '-A'])
        subprocess.check_call(['make', 'clean-typecheck'])
        subprocess.check_call(['bundle', 'exec', 'git', 'commit', '--allow-empty', '-m',
                               'Initial commit from boilerplate'])
        subprocess.check_call(['gem', 'install', 'rails', '-v', '~> 7.0'])
        parent = os.path.dirname(PROJECT_DIRECTORY)
        subprocess.check_call(['rails', 'new',
                               '--database=postgresql',
                               '--skip-test',
                               '--skip',
                               '{{cookiecutter.project_slug}}'], cwd=parent)
        if os.environ.get('SKIP_GITHUB_OP_AND_CIRCLECI_CREATION', '0') != '1':
            if subprocess.call(['op', 'item', 'get', '{{ cookiecutter.project_name }}']) != 0:
                subprocess.check_call(['op', 'item', 'create',
                                       '--category=Password',
                                       '--title={{ cookiecutter.project_name }}'])
            master_key_filename = os.path.join(PROJECT_DIRECTORY, 'config/master.key')
            with open(master_key_filename) as f:
                master_key = f.read().strip()
                subprocess.check_call(['op', 'item', 'edit',
                                       '{{ cookiecutter.project_name }}',
                                       f"master key[password]={master_key}"])
#        TODO: subprocess.check_call(['rails', 'generate', 'rspec:install'])
        subprocess.check_call(['make', 'bundle_install'])
        subprocess.check_call(['bundle', 'exec', 'rubocop', '-A'])
        subprocess.check_call(['git', 'add', '-A'])
        subprocess.check_call(['make', 'clean-typecheck'])
        subprocess.check_call(['bundle', 'exec', 'git', 'commit', '--allow-empty', '-m',
                               'rails new'])

    if os.environ.get('SKIP_GITHUB_OP_AND_CIRCLECI_CREATION', '0') != '1':
        if 'none' != '{{ cookiecutter.type_of_github_repo }}':
            if 'private' == '{{ cookiecutter.type_of_github_repo }}':
                visibility_flag = '--private'
            elif 'public' == '{{ cookiecutter.type_of_github_repo }}':
                visibility_flag = '--public'
            else:
                raise RuntimeError('Invalid argument to '
                                   'cookiecutter.type_of_github_repo: '
                                   '{{ cookiecutter.type_of_github_repo }}')
            description = "{{ cookiecutter.project_short_description.replace('\"', '\\\"') }}"
            # if repo already exists
            if subprocess.call(['gh', 'repo', 'view',
                                '{{ cookiecutter.github_username }}/'
                                '{{ cookiecutter.project_slug }}']) != 0:
                subprocess.check_call(['gh', 'repo', 'create',
                                       visibility_flag,
                                       '--description',
                                       description,
                                       '--source',
                                       '.',
                                       '{{ cookiecutter.github_username }}/'
                                       '{{ cookiecutter.project_slug }}'])
                subprocess.check_call(['gh', 'repo', 'edit',
                                       '--allow-update-branch',
                                       '--enable-auto-merge',
                                       '--delete-branch-on-merge'])
            subprocess.check_call(['git', 'push'])
            subprocess.check_call(['circleci', 'follow'])
            subprocess.check_call(['git', 'branch', '--set-upstream-to=origin/main', 'main'])
