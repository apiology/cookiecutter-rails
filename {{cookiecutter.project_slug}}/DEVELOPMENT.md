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
make ngrok
```

When done, set URL in your dependency to `${HEROKU_URL}`

## fix.sh

If you want to use rbenv/pyenv/etc to manage versions of tools,
there's a `fix.sh` script which may be what you'd like to install
dependencies. It sets `git config core.hooksPath .githooks` so tracked
bootstrap hooks apply to this repo and all its worktrees.

## Git hooks and worktrees

Bootstrap hooks live in `.githooks/` (plain bash, not Overcommit) so
`post-checkout` can run `direnv exec . ./fix.sh` on clone or
`git worktree add` before Ruby and Bundler are ready. `fix.sh` uses
helpers under `bin/`; direnv (via `.envrc`) puts `bin/` on `PATH`.

For a fresh clone with automatic bootstrap on checkout:

```sh
git clone -c core.hooksPath=.githooks <url>
```

Otherwise run `direnv exec . ./fix.sh` once after clone (or `./fix.sh` if
you have no `.envrc`) — it sets `core.hooksPath` for future worktrees.

After `git worktree add`, `.githooks/post-checkout` runs
`direnv exec . ./fix.sh` automatically when the main checkout has already
run bootstrap at least once. It writes `.ruby-version` (gitignored) and
runs `bundle install`,
so the worktree's Ruby and bundler match the main checkout. Skipping
bootstrap can cause overcommit signature mismatches even after
re-signing — see
[.cursor/rules/overcommit-signing.mdc](.cursor/rules/overcommit-signing.mdc).

## Overcommit

This project uses [overcommit](https://github.com/sds/overcommit) for
quality checks on pre-commit, pre-push, and related hooks.
`.overcommit.yml` sets `gemfile: Gemfile` so those git hooks use the
same Bundler-managed gem as `bin/overcommit`.  `bundle exec overcommit --install`
will install hooks under `core.hooksPath`. Post-checkout bootstrap is
handled by `.githooks/post-checkout`, not Overcommit.

If a commit fails with overcommit **plugin signature** or **security**
messages, run both sign commands before retrying (see
`.cursor/rules/overcommit-signing.mdc`):

```sh
bin/overcommit --sign
bin/overcommit --sign pre-commit
```

## direnv

This project uses direnv to manage environment variables used during
development.  See the `.envrc` file for detail.

### Secrets: `config/env.1p` and 1Password

`config/env.1p` in git is the **template**: each variable points at a vault
item with an `op://` [secret
reference](https://developer.1password.com/docs/cli/secret-reference), not a
plaintext value.  Load order and fallbacks are in **`.envrc`**.  Mount
**resolved** values at **`config/env.local`** (below); use **`config/env.1p`**
in git when adding or syncing `op://` keys.

For local development, you can also store **resolved** values in a
[1Password Environment](https://developer.1password.com/docs/environments/) and mount
them as a [local `.env`
file](https://developer.1password.com/docs/environments/local-env-file/) at
**`config/env.local`** (macOS beta; fifo mount, gitignored).  Do **not**
mount at `config/env.1p` — that path is the tracked `op://` template and
conflicts with git.

#### Update the Environment from `config/env.1p` (`op inject`)

```sh
op inject -i config/env.1p -o /tmp/repo-env.import -f
grep 'op://' /tmp/repo-env.import && echo 'ERROR: unresolved references' || echo 'OK'
# Import /tmp/repo-env.import in 1Password → Environments, then:
rm /tmp/repo-env.import
```

If you use a local mount at `config/env.local`, confirm
`grep -c op:// config/env.local` is **0**, then `direnv allow`.  Do not
commit `config/env.local`.
