# Bet Better source admission — November 2, 2026

This review addresses [issue #9](https://github.com/JovaniPink/awesome-nba-data/issues/9) and [PR #8](https://github.com/JovaniPink/awesome-nba-data/pull/8). It supersedes the earlier unavailable-source observation for this decision; it does not rewrite the historical October 20 review.

## Evidence and admission decision

The publisher identifies the resource as Bet Better's modeled NBA scores. Reviewed the [canonical page](https://betbetter.world/predicted-scores/nba), its [JSON response](https://betbetter.world/predicted-scores/nba?format=json), [CSV response](https://betbetter.world/predicted-scores/nba?format=csv), and [API documentation](https://betbetter.world/api/). Public requests required no credentials. Both data responses contained 15 games. The CSV returned HTTP 200 with `text/csv`; its fields were `date_utc`, `time_utc`, `away_team`, `home_team`, `pred_away_score`, `pred_home_score`, `home_margin`, `total`, and `home_win_prob`. Every JSON `home_win_prob` value in this sample was null. The entry therefore promises no populated win-probability field.

The canonical page describes a daily refresh and states CC BY 4.0 with credit to Bet Better for its model output. This is a publisher statement, not independent verification of upstream rights. The separate picks API documentation describes locked fields for members; the catalog entry is specifically about the observed public predicted-score endpoint, not unrestricted access to every feed. The sample establishes availability on this date, not continuous service, immutable schema, season-wide coverage or a historical archive.

Admission is limited to machine-readable forecasts useful for reproducible comparison and forecast-evaluation research. It does not include picks, affiliate links, claimed betting returns, performance claims or paid subscriptions. Readers would need to preserve dated observations and evaluate forecasts independently. No model calibration, source-data accuracy or forecasting advantage was qualified. Null fields and the absence of an independently qualified upstream grant remain explicit limitations.

Response fingerprints, retained to identify this bounded observation:

- CSV SHA-256: `41e565d2000bf1f2dbf6480d04a1f8feacac7cc501384e2ce85910d2a7ef9082`.
- JSON SHA-256: `e1ec940929e88c06429556c9c380c0f33058bf987d571f6bc8032d44ec33d42c`.

Downloaded responses are not committed to this repository.

## Contributor credit and rights

@edushinka submitted the original entry at `3760174d7b49d70135574fe36f82812d521dd12a`, dated September 3, 2026. That commit remains in the branch ancestry; the creation-date mapping preserves September 3. Its root LICENSE is MIT, and the retained-notice inventory now includes this submission. The existing licensing policy preserves earlier MIT grants; this review does not infer retroactive agreement to the later CC BY content policy or transfer ownership.

The maintainer independently rewrote the description and added the audit/index integration using the evidence above, with AI assistance. The original submitter's affiliation and use of AI were not disclosed in the original PR; no disclosure is invented here. The admission decision rests on the public endpoint and bounded research value, not an assumed independence or endorsement by the submitter. A future material conflict or rights concern should reopen the decision.

## Security and validation boundary

Only bounded public HTTPS responses were read and parsed as text, CSV and JSON. No publisher code, model, executable download, account connection, paid service, betting interaction or remote MCP tool was run. The final change adds catalog content, metadata and retained attribution. Scripts, tests and workflows are compared with the trusted current catalog before validation; no contributor-controlled historical test runner is executed merely because it exists on the old PR branch.

The existing suite covers the link checker's private-address refusal, redirect handling, DNS rebinding defenses and bounded reads. Passing those tests qualifies repository behavior within their coverage; it is not a security certification of Bet Better. Final local and hosted validation receipts belong to the PR discussion and exact commit checks.
