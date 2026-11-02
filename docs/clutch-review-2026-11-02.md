# Clutch inclusion decision — November 2, 2026

**Decision: include the public forecast-evaluation report in Analytics & Advanced Metrics Sites.** Its useful research purpose is inspecting evaluation methods and records, with live results distinguished from historical replay. This decision does not adopt a betting recommendation, ranking against other models, independently verified performance claim or blanket reuse permission.

The suggestion came from [@uguraltunbas in issue #22](https://github.com/JovaniPink/awesome-nba-data/issues/22), who disclosed operating Clutch and using AI assistance. The maintainer independently wrote the description and this review with AI assistance. The new URL's creation date is its first inclusion commit date, November 2; the October 24 suggestion date is not backdated into catalog metadata.

## Primary evidence

Observed November 2, 2026 unless a source date is separately stated.

| Finding | Status | Source | Date | Limit |
| --- | --- | --- | --- | --- |
| Public report separates a live graded record from a historical replay and displays probability calibration and Brier summaries | Observed report structure | [Accuracy report](https://clutchledger.com/accuracy/) | Page says updated October 31, 2026 | These remain publisher-reported results; historical replay is not prospective live evidence. |
| Published probabilities combine a proprietary model and market prices | Publisher methodology | [How it works](https://clutchledger.com/how-it-works/) | Retrieved November 2 | No independent reproduction of fitting, leakage controls, inputs or reported advantages. |
| Public downloads expressly license Clutch's own numbers under CC BY 4.0 | Observed stated grant | [Data documentation](https://clutchledger.com/data/) and [repository license](https://github.com/uguraltunbas/clutch-receipts/blob/495fe075646ab9c3b30cdf6b7eb6233f5a10ac19/LICENSE.md) | Retrieved November 2 | Market figures remain their sources' property; verification-code licensing is not established. No blanket upstream grant is inferred. |
| Accounts and paid app features are separate from the public report | Published terms | [Terms](https://clutchledger.com/terms/) | Terms dated October 26, 2026 | Terms restrict app scraping/automation. The specific public-data grant is not generalized to app access. |
| Receipt verification distinguishes GitHub push activity from author-controlled commit dates | Observed documentation | [VERIFY.md](https://github.com/uguraltunbas/clutch-receipts/blob/495fe075646ab9c3b30cdf6b7eb6233f5a10ac19/VERIFY.md) | Pinned repository revision | A hash checks a byte commitment; it alone does not establish when it became public. |

The data page and its JSON response have a later as-of basis than the October 31 report observed above. Live counts and historical backtest statistics are deliberately omitted from the catalog entry; they must not be combined into one performance estimate. GitHub's automated license label is `NOASSERTION`, so the decision uses the actual scoped LICENSE.md text, rather than assuming that metadata means no license exists.

The terms page failed through web extraction and was read with a bounded ordinary HTTPS request. Other publisher pages and GitHub files were readable through the web/connected-source tools. No publisher instructions were executed.

## Independent receipt sample

Pinned source revision: `495fe075646ab9c3b30cdf6b7eb6233f5a10ac19`. Using independently written Python standard-library checks, parsed three JSON files as data:

- `2026-27/2026-10-31/seal-232102Z.json`.
- `2026-27/2026-10-31/seal-235116Z.json`.
- `2026-27/2026-10-31/reveal-081828Z.json`.

All three SHA-256 values matched the pinned index; the two adjacent chain links matched. Seven revealed openings matched commitments in the two sampled seals. No downloaded verification script was run and no receipt contents or model data are republished here.

GitHub PushEvent `25953783682` records head `0482885acb09b2736154db94c4f03bd727e296a6` at `2026-10-31T23:51:20Z`. The later seal's bytes at that head matched the sampled hash. The server event time precedes all four scheduled tip times listed in that seal. Those scheduled times are publisher fields, not independently verified actual starts. This one-event sample establishes neither the entire history's timing nor a complete outcome/accuracy audit. A chain can be internally consistent without independently witnessed publication times.

## Security and remaining limits

Only public HTML and small, pinned JSON/text files were read. Paths were constrained before retrieval; parsing used our own code and standard libraries. No third-party verification code, app, account, payment, model or remote tool was installed or executed. No credentials were sent to the publisher. Source review does not certify service security, forecasting fitness, market-data rights or continuous availability.

The earlier request for receipt/code licensing does not need to hold website inclusion: the current number-specific grant is explicit, code reuse is not required, and the entry makes the scope visible. Full-history timing and performance replication, verification-code reuse and intended downstream ingestion rights remain separate questions. Catalog inclusion grants none of them. Existing generated schema and historical catalog-wide review dates remain unchanged; the audit row and this record carry the bounded source review.
