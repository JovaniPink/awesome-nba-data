# Keel Stats and StatsNext source review

Checked 2026-11-25. This is a bounded publisher-documentation review, not a
catalog-wide freshness review, authenticated API test, or data-admission decision.
Public pages were readable through the research retrieval service; no account,
MCP connection, paid access, bulk export, or independent recomputation was used.
No numeric HTTP status is inferred from the rendered-page retrieval.

## Keel Stats access correction

Canonical URL: <https://keelstats.com/nba/leaders>.
Credit: @symonovserhii, affiliated contributor, [issue #28](https://github.com/JovaniPink/awesome-nba-data/issues/28)
and [November 22 revision](https://github.com/JovaniPink/awesome-nba-data/issues/28#issuecomment-7075384551).

- The public leaders page presents NBA statistics. The [methodology](https://keelstats.com/methodology)
  separately describes Keel's ratings and projections. Their model quality and
  historical information availability were not independently qualified.
- The [MCP documentation](https://keelstats.com/mcp) documents limited access
  without an account: current/previous seasons and games within two weeks of
  today, with tool-specific differences. A free account expands history; Pro
  unlocks additional tools. This supports correcting the old blanket account
  requirement, not claiming that every tool works anonymously.
- [Use our data](https://keelstats.com/press) permits credited editorial use of
  Keel-created charts and numbers and withholds raw downloads/bulk exports.
  [Terms](https://keelstats.com/terms), updated November 8, 2026, restrict bulk
  copying, scraping and resale. Provider statements do not grant third-party
  feed rights. Existing reuse caveats remain.

Decision: update the existing entry. Preserve its URL, stable identity and
2026-11-02 creation date. MCP execution, exact endpoint coverage, correction
history and model accuracy remain untested.

## StatsNext analytical website

Canonical URL: <https://statsnext.com/nba/defense-vs-position>.
Credit: @CatalystPit, disclosed owner, [issue #31](https://github.com/JovaniPink/awesome-nba-data/issues/31).

The page displayed current-season per-game and per-100-possession tables, sample
counts and dates; its displayed coverage ran through November 23 and its update
date was November 25. The publisher describes observed box-score aggregation,
not forecasts. Listed-position grouping excludes dual-position players from
the positional tables while retaining them in team totals. Opponent mix and
small samples limit comparisons; the numbers are not opponent-adjusted.

The page's citation notice permits free reading/linking and asks for its URL and
update date when citing a figure. It expressly does not authorize dataset
redistribution. [Terms](https://statsnext.com/terms), effective October 15, 2026,
do not include API, bulk-download, resale or commercial redistribution rights
with consumer access. Separate written terms are needed for data arrangements.
No open-data license is inferred. This sports-research publisher also offers
betting-related products; this entry is limited to the statistical reference.

Decision: add a qualified analytical-site entry. Record 2026-11-25 as its first
catalog-addition date. API/export access, dataset accuracy and reuse permission
for ingestion remain unqualified. No existing source-matrix row is affected.

## Change and validation boundary

The README, per-source audit and generated index must agree. Historical catalog
review/projection dates and unrelated source assessments remain unchanged.
Material AI assistance: research, original summaries and implementation were
prepared with an AI assistant; source claims are bounded by the linked evidence.
