# Catalog review - October 20, 2026

This is an automated transport audit plus targeted public-source content review. It is
not a catalog-wide human review, dataset-quality qualification, or license grant. Existing
catalog-wide review dates and schema 1.1 uncertainty defaults remain unchanged.

## Review basis

- Baseline: `3dcedc2b9bf91adcdccb9b8d4461304afdd12388`.
- No open contributor PRs at review time. Previously integrated resources from PRs #11
  and #12 remain intact through the existing #13 integration.

## Targeted findings

| Source | October 20 evidence | Change and limitation |
| --- | --- | --- |
| [NBA injury reports](https://official.nba.com/nba-injury-report-2026-27-season/) | The old 2025-26 URL redirects to the 2026-27 page; direct GET returned 200 with the new season title. | Updated README, source audit, matrix, and contract tests. This is a changing document reference, not a historical bulk API or permission to redistribute. |
| FiveThirtyEight RAPTOR article and NBA tag page | Both returned HTTP 200 after redirecting to ABC News politics, unrelated to the promised resource. | Replaced the two listings with one [publisher RAPTOR CSV archive](https://github.com/fivethirtyeight/data/tree/master/nba-raptor). Its field documentation explains differences between historical and tracking-era model inputs; it is not the original methodology article. |
| [Kaggle NBA search](https://www.kaggle.com/search?q=NBA+dataset) | The implemented checker initially observed HEAD 404, while a subsequent direct GET returned 200 with the Search title. | Retained the entry; added GET confirmation for HEAD 404/410 and a regression test. This is another reason not to equate a status-only result with a dead resource. |

The initial 47-entry scan had two HTTP 403 responses. Other resources' historical audit
rows were not relabeled as freshly reviewed simply because their URLs responded.

[Issue #9](https://github.com/JovaniPink/awesome-nba-data/issues/9) refers to BetBetter
PR #8, but authenticated GitHub REST and GraphQL lookup returned not found. That source
is absent from the published README. Provenance and admission remain unresolved; this
integration does not close the issue or assert its acceptance criteria are satisfied.

[License issue #2](https://github.com/JovaniPink/awesome-nba-data/issues/2) remains open.
[Renovate #14](https://github.com/JovaniPink/awesome-nba-data/pull/14) remains separate;
its existing hosted Python 3.11/3.14 checks passed at review time.

## Validation and boundaries

Run the canonical commands from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_readme.py README.md
python3 scripts/build_resource_index.py --check
python3 scripts/audit_links.py --output /tmp/catalog-link-audit.json
```

The offline suite includes controlled-response tests for redirects to unrelated HTTP 200
pages, HEAD rejection and false 404 responses, blocked requests, rate limits, missing
responses, transient errors, redirect loops, bounded GET bodies, and catalog preservation.
The live audit is deliberately outside CI. Its JSON records each request and observation;
HTTP success alone does not verify content, freshness, rights, or current data coverage.

Existing resource identifiers and creation dates were compared with the baseline. All
surviving identities retain their dates. Replacement URLs get new identities with explicit
October 20 inclusion dates; older URL dates remain in configuration as historical metadata.
Contributor-supplied identity dates remain attached to their original commits.

Original contributor PRs, Renovate onboarding, and open issues are unchanged. No merge,
contributor feedback, license change, paid API access, or dataset import is part of this
integration. Source descriptions based on public documentation do not establish
independently tested authenticated behavior. Hosted CI on these local integration commits
has not run.

## Final integration check

- Offline unit suite: 38 tests passed; README validation, generated-index check, and whitespace check passed.
- Final automated scan: 46 entries; blocked/authentication-required: 1, reachable: 41, redirected: 4.
- Observation interval: `2026-10-20T19:31:13+00:00` through `2026-10-20T19:31:19+00:00`.
- [Full link-audit JSON](link-audits/2026-10-20.json) includes the matching catalog SHA-256 and per-request evidence.
- Redirects and blocks remain review observations, not proof of content relevance or dead links.
