# Development

## Running database via Docker on MacOS

```sh
make docker
```

## Running application locally

1. `make docker`
2. `M-x rename-buffer *{{cookiecutter.project_slug}}*`
3. `rails server`
4. `M-x shell`
5. `curl http://localhost:3000/checks/shave_yaks/actions | jq .`

## Running Rails stuff via docker-compose

1. `M-x shell`
2. `M-x rename-buffer *docker-compose*`
3. `open /Applications/Docker.app && while ! docker pull ubuntu; do sleep 1; done`
4. `make docker-web`
5. `M-x shell`
6. `curl http://localhost:3000/whatever | jq .`

## fix.sh

If you want to use rbenv/pyenv/etc to manage versions of tools,
there's a `fix.sh` script which may be what you'd like to install
dependencies.

## Overcommit

This project uses [overcommit](https://github.com/sds/overcommit) for
quality checks.  `bundle exec overcommit --install` will install it.

## direnv

This project uses direnv to manage environment variables used during
development.  See the `.envrc` file for detail.
