# Browser source review — October 20, 2026

Targeted browser content checks followed the hardened automated link audit. This is
not a catalog-wide human review, data-quality assessment, or permission to scrape.
Existing catalog-wide review dates and resource creation dates are preserved.

## Confirmed URL corrections

| Previous URL | Verified destination and content | Change |
| --- | --- | --- |
| `https://www.breakthroughbasketball.com/stats/effective-field-goal-percentage.html` | [Effective Field Goal Percentage](https://www.breakthroughbasketball.com/stats/effective-field-goal-percentage) loads the basketball explainer in the browser. | Remove `.html` from the canonical URL. The old URL redirected; its automated 403 was not proof of deletion. |
| `https://backpicks.com/` | [Thinking Basketball](https://thinkingbasketball.net/) contains Ben Taylor's current posts, metrics navigation, and historical series. Some articles require Patreon membership. | Update the name and canonical URL, and move the entry from Legacy to Analytics. |

Each replacement URL receives a new resource identity with an explicit 2026-10-20
creation date. Old URL date mappings remain in configuration. The two corresponding
source-audit rows record browser content verification, rather than an inferred HTTP
status. All 46 catalog entries retain matching audit rows.

## Access uncertainty and archives

- [Stathead basketball](https://stathead.com/basketball/) redirected to Sports
  Reference's Stathead destination and displayed a bot-verification screen. Paid
  query access remains untested. Retain the listing; no evidence establishes a dead
  resource, and no challenge was solved.
- [FiveThirtyEight's RAPTOR folder](https://github.com/fivethirtyeight/data/tree/master/nba-raptor)
  remains the existing publisher-hosted historical option. Its documentation
  distinguishes modern tracking-era files from historical estimates using different
  inputs. It is not a replacement for current-season data. Pin a specific repository
  revision and inspect the applicable terms when reusing files.

No replacement mirror was added for a working publisher page. Browser access and a
successful HTTP response do not establish complete data coverage or reuse rights.

## Validation

The 62-test suite, README validation, generated-index check, and whitespace check
passed. The catalog still has 46 entries. Existing identities' creation dates and
the historical projection date were compared with the branch baseline and retained.
The link checker and its security policy are unchanged.

A targeted hardened-checker rerun returned HTTP 200 without redirects for both new
canonical URLs. This corroborates reachability; the browser checks above establish
the inspected page content.
