#!/usr/bin/env python

import os
import subprocess
import sys
import tempfile
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
    subprocess.check_call(*args, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, **kwargs)


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


def verify_backup_file(filename):
    orig_filename = filename[:-1]
    new_filename = filename
    print("Verifying backup file", filename)

    # if two files are identical, remove new one
    with open(orig_filename) as f:
        orig_contents = f.read()
    with open(new_filename) as f:
        new_contents = f.read()
    if orig_contents == new_contents:
        run(['rm', new_filename])
        return

    errmsg = f'Found a file ending in ~: {filename}'
    # add the contents of old file and new file
    # to the error message
    errmsg += '\n'
    errmsg += f'Old file: {orig_filename}\n'
    with open(orig_filename) as f:
        errmsg += f.read()
    errmsg += '\n'
    errmsg += f'New file: {new_filename}\n'
    with open(new_filename) as f:
        errmsg += f.read()
    errmsg += f"Diff between files - save to {orig_filename}.patch\n"
    # add diff to errmsg
    errmsg += subprocess.getoutput(f'diff -u {orig_filename} {new_filename}')
    raise RuntimeError(errmsg)


def verify_directory(directory):
    for root, dirs, files in os.walk(directory):
        if big_and_irrelevant_directory(root):
            continue
        for filename in files:
            if filename.endswith('~'):
                full_filename = os.path.join(root, filename)
                verify_backup_file(full_filename)


def big_and_irrelevant_directory(root):
    return root.startswith('./.git') or root.startswith('./tmp/cache')


def patch_directory(directory):
    for root, dirs, files in os.walk(directory):
        if big_and_irrelevant_directory(root):
            continue

        for filename in files:
            if filename.endswith('.patch'):
                try:
                    full_filename = os.path.join(root, filename)
                    original_filename = full_filename[:-6]
                    run(['patch', '-f', '-i', full_filename])
                    # delete file
                    run(['rm', full_filename])
                except subprocess.CalledProcessError:
                    print(f'Error patching using {full_filename}')
                    with open(original_filename) as f:
                        original_file_contents = f.read()
                    print(f'File being patched:\n{original_file_contents}',
                          flush=True, file=sys.stdout)
                    orig_file = f"{original_filename}.orig"
                    with open(orig_file) as f:
                        orig_file_contents = f.read()
                    print(f'Original file:\n{orig_file_contents}',
                          flush=True, file=sys.stdout)
                    rej_file = f"{original_filename}.rej"
                    with open(rej_file) as f:
                        rej_file_contents = f.read()
                    print(f'Rejected hunk:\n{rej_file_contents}',
                          flush=True, file=sys.stdout)
                    raise


if __name__ == '__main__':
    if 'Not open source' == '{{ cookiecutter.open_source_license }}':
        remove_file('LICENSE')
        remove_file('CONTRIBUTING.rst')

    if 'Yes' != '{{ cookiecutter.use_checkoff }}':
        remove_file('config/initializers/checkoff.rb')

    if os.environ.get('SKIP_GIT_CREATION', '0') != '1':
        # Don't run these non-idempotent things when in
        # cookiecutter_project_upgrader, which will run this hook
        # multiple times over its lifetime.
        run(['git', 'init'])
    parent = os.path.dirname(PROJECT_DIRECTORY)
    # https://guides.rubyonrails.org/upgrading_ruby_on_rails.html
    # Make this configurable?
    run(['gem', 'install', 'rails', '-v', '~> 7.2.1'],
        cwd=parent)
    run(['rbenv', 'version'],
        cwd=parent)
    if os.environ.get('SKIP_RAILS_NEW', '0') != '1':
        # with a temporary directory
        with tempfile.TemporaryDirectory() as tempdir:
            run(['rbenv', 'exec', 'rails', 'new',
                 '--database=postgresql',
                 '--skip-test',
                 '--skip',
                 '{{cookiecutter.project_slug}}'], cwd=tempdir)
            run(['rm', '-rf', os.path.join(tempdir, '{{cookiecutter.project_slug}}', '.git')])
            # copy artifacts back
            run(['gcp', '-R', '--backup',
                 os.path.join(tempdir, '{{cookiecutter.project_slug}}', '.'),
                 PROJECT_DIRECTORY])
            revert = [
                '.rubocop.yml',
                'README.md',
                '.gitignore',
                '.ruby-version',
            ]

            # revert from the backup file, as these files don't have
            # interesting upstream information for us
            for filename in revert:
                run(['mv', f'{filename}~', filename])

            # find all files ending in .patch
            patch_directory('.')

            # error out if we find any files that end in '~' recursively
            verify_directory('.')

    run('./fix.sh')
    run(['git', 'add', '-A'])
    run(['bundle', 'exec', 'overcommit', '--install'])
    run(['bundle', 'exec', 'overcommit', '--sign'])
    run(['bundle', 'exec', 'overcommit', '--sign', 'pre-commit'])
    run(['make', 'bundle_install'])
    run(['bundle', 'exec', 'rubocop', '-A'])
    run(['git', 'add', '-A'])
    run(['make', 'build-typecheck'])
    run(['bundle', 'exec', 'git', 'commit', '--allow-empty',
         '-m', 'Initial commit from boilerplate'])

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
    # update frequently security-flagged gems
    run(['bundle', 'update', '--conservative',
         'rexml', 'rails', 'puma', 'nokogiri'])
    run(['rails', 'g', 'rspec:install', '--skip'])
    run(['rails', 'importmap:install'])
    run(['rails', 'g', 'annotate:install', '--skip'])
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
                run(['heroku', 'create', '{{ cookiecutter.project_slug }}'])
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
