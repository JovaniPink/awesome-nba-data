# Keel Stats inclusion decision — November 2, 2026

**Decision: include the public NBA analytical website in Analytics & Advanced Metrics Sites.** Statistical comparisons and documented derived metrics meet the catalog's research-value standard. This is a website reference, with access and reuse qualifications; it does not approve a raw feed, an authenticated connector or a forecasting claim.

Credit: [@symonovserhii's issue #24](https://github.com/JovaniPink/awesome-nba-data/issues/24), which disclosed affiliation with the service. The maintainer independently wrote this review and catalog description with AI assistance. No AI-use statement is invented for the submitter. The canonical URL's creation date is November 2, the first inclusion commit date; the November 1 suggestion date remains in the issue history.

## Primary evidence

All observations retrieved November 2, 2026. These are source-specific observations, not a catalog-wide review.

| Finding | Status | Source | Date | Limit |
| --- | --- | --- | --- | --- |
| Public NBA statistics and analytical views can be read without logging in | Observed pages | [Leaders](https://keelstats.com/nba/leaders), [usage](https://keelstats.com/nba/usage), [defense vs position](https://keelstats.com/nba/defense) | November 2 | A sampled page read does not verify feed accuracy, completeness, latency or every feature's access. |
| Proprietary derived ratings and projections have published descriptions | Observed methodology, implementation claims remain publisher assertions | [Methodology](https://keelstats.com/methodology) | November 2 | Methods, inputs, fit, leakage controls and claimed validation were not independently reproduced. Observed statistics and modeled quantities must remain distinguishable. |
| Public documentation describes account-authorized MCP access with free and Pro features | Observed documentation | [MCP documentation](https://keelstats.com/mcp) | November 2 | No OAuth/token flow, tool execution, account permission or runtime read-only guarantee was independently tested. |
| Credited editorial use of the service's own charts/cards/numbers is expressly permitted | Observed stated permission | [Use our data](https://keelstats.com/press) | November 2 | This is narrower than a general open-data or bulk-redistribution license and does not establish rights to upstream feed data. |
| Raw data distribution and bulk copying/scraping are restricted | Observed stated restrictions | [Terms](https://keelstats.com/terms) and [Use our data](https://keelstats.com/press) | Terms dated October 18, 2026 | Restrictions must be assessed for the intended use. A public page or MCP account is not a downstream ingestion grant. |

The terms name FOP Symonov Serhii as the operator and disclaim NBA/NFL affiliation. The press page identifies balldontlie as its provider for scores, box scores, play by play, injury reports and sportsbook lines. Those are publisher disclosures; no vendor contract was inspected.

## Research and access decision

The useful catalog scope is comparing basketball statistics and learning about derived methods. No picks, affiliate links, performance rankings or unsupported claim of model superiority is included. Early-season sample sizes and feed corrections remain material limitations; no current numerical leaderboard or forecast result is copied into the entry.

The press page says the service does not offer raw downloads, bulk exports or access to its API, while the separate MCP documentation describes an authenticated analytical interface. These are different documented access surfaces. Neither statement is expanded into a claim of a generally accessible raw API or permission to extract its underlying data. The entry states account requirements and feature tiers; it does not provide installation instructions or endorse a connector configuration.

Our earlier comment described reuse restrictions broadly. The current decision additionally recognizes the positive editorial permission: attributed use of Keel's own charts and numbers is allowed by its press page. No change to those terms is required to list this website, and the contributor does not need to prepare metadata or a PR for the maintainer's inclusion decision.

## Security and verification limits

Only the public documentation and a few public reference pages were read. No crawling of statistical records, bulk extraction, downloaded executable, remote MCP request, account, OAuth authorization, personal token, paid subscription or free Pro activation was used. Publisher instructions and example configuration were treated as documentation, not executed.

The catalog change uses the existing schema/generator and consists of original prose, source audit, explicit inclusion date, generated record and suggestion credit. Scripts, tests, dependencies and workflow permissions remain unchanged. Existing tests verify repository destination controls within their coverage; they cannot certify the provider's infrastructure or tool behavior. Authenticated MCP behavior, data correctness, proprietary model validation and downstream reuse rights remain unqualified. They are separate questions for any proposed integration, not prerequisites for this qualified analytical website reference.
