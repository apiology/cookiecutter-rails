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
5. `curl http://localhost:3000/whatever`

## Running Rails stuff via docker-compose

1. `M-x shell`
2. `M-x rename-buffer *docker-compose*`
3. `open /Applications/Docker.app && while ! docker pull ubuntu; do sleep 1; done`
4. `make docker-web`
5. `M-x shell`
6. `curl http://localhost:3000/whatever`

## Running everything (including job processing) via docker-compose

1. `M-x shell`
2. `M-x rename-buffer *docker-compose*`
3. `make docker-all`
4. `M-x shell`
5. `curl http://localhost:3000/whatever`

## Hitting with curl

Note: Production URL is `${HEROKU_URL}`

```sh
curl --verbose --fail http://localhost:3000/whatever
```

```sh
curl --verbose --fail -H "Content-Type: application/json" -d '{"foo": {"bar": 123}}' -X POST http://localhost:3000/whatever
```

```sh
curl --verbose --fail http://localhost:3000/foo/bar
```

## Logging

To set log level in Heroku:

```sh
heroku config:set LOG_LEVEL=INFO # other values: DEBUG, ...
```

You can set `LOG_LEVEL` locally as well.

## Setting up ngrok

```sh
# M-x shell
# M-x rename-buffer *ngrok*
ngrok http http://localhost:3000 # brew install ngrok/ngrok/ngrok
# Go to http://127.0.0.1:4040/status or https://dashboard.ngrok.com/cloud-edge/endpoints to get endpoints
```

When done, set URL in your dependency to `${HEROKU_URL}`

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
