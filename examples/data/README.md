# Lab data

| File | What it is |
| --- | --- |
| `fiction_briefs.json` | Sixteen original fictional Danish briefs (`lab-01` … `lab-16`) |
| `error_items.json` | Fourteen typed hop-error fixtures |
| `fiction_articles.csv` | Same briefs with the 2023 `article text` header |

Regenerate from the in-module corpus:

```bash
python3 -m silverlab export-data
```

Nothing here is scraped news. Ids stay in the `lab-*` / `err-*` namespaces
so they do not collide with sample ids on other personal-docs branches.
