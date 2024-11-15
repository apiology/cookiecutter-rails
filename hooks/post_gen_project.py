#!/usr/bin/env python

import os
import subprocess
from urllib.parse import urlparse

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)

port_prefix_str = '{{cookiecutter.db_port_prefix}}'
port_prefix = int(port_prefix_str) * 10


def run(*args, **kwargs):
    if len(kwargs) > 0:
        print('running with kwargs', kwargs, ':', *args, flush=True)
    else:
        print('running', *args, flush=True)
    # keep both streams in the same place so that we can weave
    # together what happened on report instead of having them
    # dumped separately
    subprocess.check_call(*args, stderr=subprocess.STDOUT, **kwargs)


def remove_file(filepath):
    os.remove(os.path.join(PROJECT_DIRECTORY, filepath))


def onepass_entry_exists(onepass_entry):
    return subprocess.call(['op', 'item', 'get', onepass_entry]) == 0


def create_onepass_entry(onepass_entry):
    run(['op', 'item', 'create',
         '--category=Login',
         f'--title={onepass_entry}'])


def add_onepass_password_field(onepass_entry, password, password_field='password'):
    add_onepass_field(onepass_entry, password_field, password, field_type='password')


def add_onepass_field(onepass_entry, field_name, field_value, field_type='string'):
    run(['op', 'item', 'edit',
         onepass_entry,
         f'{field_name}[{field_type}]={field_value}'])


def create_onepass_db(onepass_entry, password, database,
                      password_field='password', port=5432, server=None):
    if not onepass_entry_exists(onepass_entry):
        create_onepass_entry(onepass_entry)
        add_onepass_password_field(onepass_entry, password)
        add_onepass_field(onepass_entry, 'port', port)
        add_onepass_field(onepass_entry, 'username',
                          "{{ cookiecutter.project_slug.replace('-', '_') }}")
        add_onepass_field(onepass_entry, 'database', database)
        if server is not None:
            add_onepass_field(onepass_entry, 'server', server)


def random_password():
    return subprocess.check_output(['openssl', 'rand', '-base64', '32']).decode().strip()


def create_production_db_onepass_entry():
    onepass_entry = '{{ cookiecutter.project_slug }} production database'
    if not onepass_entry_exists(onepass_entry):
        create_onepass_entry(onepass_entry)


def create_docker_compose_db_onepass_entry(rails_env, port):
    database = "{{ cookiecutter.project_slug.replace('-', '_') }}_" f'{rails_env}'
    create_onepass_db('{{ cookiecutter.project_slug }} '
                      f'local {rails_env} docker-compose database - {database}',
                      password=random_password(), port=port,
                      server='localhost',
                      database=database)


if __name__ == '__main__':
    if 'Not open source' == '{{ cookiecutter.open_source_license }}':
        remove_file('LICENSE')
        remove_file('CONTRIBUTING.rst')

    if 'Yes' != '{{ cookiecutter.use_checkoff }}':
        remove_file('config/initializers/checkoff.rb')

    run('./fix.sh')
    if os.environ.get('IN_COOKIECUTTER_PROJECT_UPGRADER', '0') == '1':
        os.environ['SKIP_GIT_CREATION'] = '1'
        os.environ['SKIP_EXTERNAL'] = '1'

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
        run(['make', 'build-typecheck'])
        run(['bundle', 'exec', 'git', 'commit', '--allow-empty', '-m',
             'Initial commit from boilerplate'])

        parent = os.path.dirname(PROJECT_DIRECTORY)
        # https://guides.rubyonrails.org/upgrading_ruby_on_rails.html
        # Make this configurable?
        run(['gem', 'install', 'rails', '-v', '~> 7.2.1'],
            cwd=parent)
        run(['rbenv', 'version'],
            cwd=parent)
        run(['rbenv', 'exec', 'rails', 'new',
             '--database=postgresql',
             '--skip-test',
             '--skip',
             '{{cookiecutter.project_slug}}'], cwd=parent)
        if os.environ.get('SKIP_EXTERNAL', '0') != '1':
            main_onepass_entry = '{{ cookiecutter.project_name }}'
            if not onepass_entry_exists(main_onepass_entry):
                master_key_filename = os.path.join(PROJECT_DIRECTORY, 'config/master.key')
                with open(master_key_filename) as f:
                    master_key = f.read().strip()
                create_onepass_entry(main_onepass_entry)
                add_onepass_password_field(main_onepass_entry,
                                           master_key,
                                           password_field='master key')
            create_docker_compose_db_onepass_entry('dev', port=port_prefix + 2)
            create_docker_compose_db_onepass_entry('test', port=port_prefix + 3)
            create_production_db_onepass_entry()
        run(['make', 'bundle_install'])
        run(['rails', 'g', 'rspec:install'])
        run(['bundle', 'exec', 'rubocop', '-A'])
        run(['git', 'add', '-A'])
        run(['make', 'build-typecheck'])
        run(['bundle', 'exec', 'git', 'commit', '--allow-empty', '-m',
                               'rails new'])

    if os.environ.get('SKIP_EXTERNAL', '0') != '1':
        heroku_app_name = '{{ cookiecutter.project_slug }}'

        if '{{ cookiecutter.deploy_to_heroku }}' == 'yes':
            # run "heroku ps" to see if this already exists
            if subprocess.call(['heroku', 'ps', '-a', heroku_app_name]) != 0:
                run(['heroku', 'create'])
            # check for heroku_rediscloud
            if '{{ cookiecutter.heroku_rediscloud }}' == 'yes':
                if subprocess.call(['heroku', 'config:get', 'REDISCLOUD_URL',
                                    '-a', heroku_app_name]) != 0:
                    run(['heroku', 'addons:add', 'rediscloud', '-a', heroku_app_name])
                heroku_entry_name = '{{ cookiecutter.project_name }} redis'
                if not onepass_entry_exists(heroku_entry_name):
                    redis_url = subprocess.check_output(['heroku', 'config:get',
                                                         'REDISCLOUD_URL',
                                                         '-a', heroku_app_name]).decode().strip()
                    # parse redis_url with library
                    parsed_url = urlparse(redis_url)
                    user = parsed_url.username
                    host = parsed_url.hostname
                    port = parsed_url.port
                    password = parsed_url.password
                    create_onepass_entry(heroku_entry_name)
                    add_onepass_field(heroku_entry_name, 'username', user)
                    add_onepass_field(heroku_entry_name, 'hostname', host)
                    add_onepass_field(heroku_entry_name, 'port', port)
                    add_onepass_password_field(heroku_entry_name, password)
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
            # if repo doesn't already exist
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
