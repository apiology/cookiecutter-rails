#!/usr/bin/env python

import os
import subprocess

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def run(*args, **kwargs):
    if length(kwargs) > 0:
        print('running with kwargs', kwargs, ":", *args)
    else:
        print('running', *args)
    subprocess.check_call(*args, **kwargs)


def remove_file(filepath):
    os.remove(os.path.join(PROJECT_DIRECTORY, filepath))


def onepass_entry_exists(onepass_entry):
    return subprocess.call(['op', 'item', 'get', onepass_entry]) == 0


def create_onepass_entry(onepass_entry):
    run(['op', 'item', 'create',
                           '--category=Login',
                           f'--title={onepass_entry}'])

def add_onepass_password_field(onepass_entry, password, password_field='password'):
	run(['op', 'item', 'edit',
                           onepass_entry,
                           f"{password_field}[password]={password}"])

def add_onepass_field(onepass_entry, field_name, field_value):
	run(['op', 'item', 'edit',
                           onepass_entry,
                           f"{field_name}={field_value}"])


def create_onepass_db(onepass_entry, password, database, password_field='password', port=5432, server=None):
    if not onepass_entry_exists(onepass_entry):
        create_onepass_entry(onepass_entry)
        add_onepass_password_field(onepass_entry, password)
        add_onepass_field(onepass_entry, 'port', port)
        add_onepass_field(onepass_entry, 'username', "{{ cookiecutter.project_slug.replace('-', '_') }}")
        add_onepass_field(onepass_entry, 'database', database)
        if server is not None:
            add_onepass_field(onepass_entry, 'server', server)



def random_password():
    return subprocess.check_output(['openssl', 'rand', '-base64', '32']).decode().strip()


def create_production_db_onepass_entry():
    onepass_entry = "{{ cookiecutter.project_slug }} production database"
    if not onepass_entry_exists(onepass_entry):
        create_onepass_entry(onepass_entry)


def create_docker_compose_db_onepass_entry(rails_env, port):
    database = "{{ cookiecutter.project_slug.replace('-', '_') }}_" f"{rails_env}"
    create_onepass_db('{{ cookiecutter.project_slug }} ' f"local {rails_env} docker-compose database - {database}",
                      password=random_password(), port=port,
                      server='localhost',
                      database=database)


if __name__ == '__main__':
    if 'Not open source' == '{{ cookiecutter.open_source_license }}':
        remove_file('LICENSE')
        remove_file('CONTRIBUTING.rst')

    run('./fix.sh')
    if os.environ.get('IN_COOKIECUTTER_PROJECT_UPGRADER', '0') == '1':
        os.environ['SKIP_GIT_CREATION'] = '1'
        os.environ['SKIP_GITHUB_OP_AND_CIRCLECI_CREATION'] = '1'

    if os.environ.get('SKIP_GIT_CREATION', '0') != '1':
        # Don't run these non-idempotent things when in
        # cookiecutter_project_upgrader, which will run this hook
        # multiple times over its lifetime.
        run(['git', 'init'])
        run(['git', 'add', '-A'])
        run(['bundle', 'exec', 'overcommit', '--install'])
        run(['bundle', 'exec', 'overcommit', '--sign'])
        run(['bundle', 'exec', 'overcommit', '--sign', 'pre-commit'])
        run(['make', 'bundle_install'])
        run(['bundle', 'exec', 'rubocop', '-A'])
        run(['git', 'add', '-A'])
        run(['make', 'clean-typecheck'])
        run(['bundle', 'exec', 'git', 'commit', '--allow-empty', '-m',
                               'Initial commit from boilerplate'])
        parent = os.path.dirname(PROJECT_DIRECTORY)
        run(['gem', 'install', 'rails', '-v', '~> 7.0'],
                              cwd=parent)
        run(['rbenv', 'version'],
                              cwd=parent)
        run(['rbenv', 'exec', 'rails', 'new',
                               '--database=postgresql',
                               '--skip-test',
                               '--skip',
                               '{{cookiecutter.project_slug}}'], cwd=parent)
        if os.environ.get('SKIP_GITHUB_OP_AND_CIRCLECI_CREATION', '0') != '1':
            main_onepass_entry = '{{ cookiecutter.project_name }}'
            if not onepass_entry_exists(main_onepass_entry):
                master_key_filename = os.path.join(PROJECT_DIRECTORY, 'config/master.key')
                with open(master_key_filename) as f:
                    master_key = f.read().strip()
                create_onepass_entry(main_onepass_entry)
                add_onepass_password_field(main_onepass_entry, master_key, password_field='master key')
            create_docker_compose_db_onepass_entry('dev', port={{cookiecutter.db_port_prefix}}2) # noqa: E999
            create_docker_compose_db_onepass_entry('test', port={{cookiecutter.db_port_prefix}}3) # noqa: E999
            create_production_db_onepass_entry()
        run(['make', 'bundle_install'])
        run(['bundle', 'exec', 'rubocop', '-A'])
        run(['git', 'add', '-A'])
        run(['make', 'clean-typecheck'])
        run(['bundle', 'exec', 'git', 'commit', '--allow-empty', '-m',
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
                run(['gh', 'repo', 'create',
                                       visibility_flag,
                                       '--description',
                                       description,
                                       '--source',
                                       '.',
                                       '{{ cookiecutter.github_username }}/'
                                       '{{ cookiecutter.project_slug }}'])
                run(['gh', 'repo', 'edit',
                                       '--allow-update-branch',
                                       '--enable-auto-merge',
                                       '--delete-branch-on-merge'])
            run(['git', 'push'])
            run(['circleci', 'follow'])
            run(['git', 'branch', '--set-upstream-to=origin/main', 'main'])
