# Hooks

Git doesn't copy hooks when a repository is cloned, so they're kept here and
installed by hand:

```bash
cp hooks/pre-commit hooks/commit-msg .git/hooks/
```

- `pre-commit` blocks credentials, keys, other people's email addresses, key
  or secrets files, and live ledgers or private research material. It runs
  `mind/tests` once they exist.
- `commit-msg` blocks email addresses and tokens in commit messages.

Neither hook holds a private string. Personal names and addresses are blocked
by a separate machine-wide guard that reads its patterns from a file outside
every repository.
