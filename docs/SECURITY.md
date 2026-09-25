# Repository hygiene

Before each public push:

1. Run `git status` and review every file.
2. Keep `config.json`, `.env`, cookies, browser profiles and local datasets out of Git.
3. Search staged content for passwords, API keys, tokens and private e-mail addresses.
4. Never commit production spreadsheet templates or downloaded editorial media unless explicitly cleared for publication.

Example PowerShell review:

```powershell
git diff --cached --name-only
git diff --cached
```
