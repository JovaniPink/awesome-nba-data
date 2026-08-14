# NBA programmatic source matrix

_Reviewed: 2026-08-13_

This matrix is a discovery and governance aid, not legal advice or an approval record. `Unknown`
means the reviewed public material did not establish permission for NBA Lab's exact private,
practice-credit, market-adjacent use. No source below is approved for live NBA Lab ingestion.

| Source | Observed coverage | Access and cadence | Bulk and identifiers | Storage / redistribution | Modeling | Market-adjacent use | NBA Lab status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NBA.com / NBA Stats | Official schedules, scores, box scores, play-by-play, shooting, lineup, and tracking summaries; endpoint history varies | Public web surfaces; no published external API stability or bulk contract | Per-request NBA identifiers; no documented supported bulk export | Restricted by NBA terms; comprehensive regularly updated databases require consent | Unknown for the intended workflow | NBA terms prohibit use of NBA Statistics in connection with gambling activity | **Not approved** |
| `nba_api` | Community mappings for NBA.com Stats and live-data endpoints | Open-source client; upstream endpoints change or disappear | Request-oriented; uses NBA identifiers | MIT applies to client code, not upstream NBA data | Inherits upstream uncertainty | Inherits upstream uncertainty | **Probe only** |
| hoopR / SportsDataverse NBA releases | Processed NBA play-by-play advertised from 2002 onward; source families include ESPN and NBA Stats | Public R package and seasonal data releases; current site shows 2002-2026 loaders | Bulk release assets; mixed NBA/ESPN identifiers | Package code is open; dataset-specific upstream rights remain unknown | Unknown | Unknown | **Not approved** |
| `sportsdataverse-py` | NBA schedules, play-by-play, box scores, rosters, standings, and source wrappers | Public Python package; source-specific refresh behavior | Wrapper and loader surfaces; mixed provider identifiers | Package license does not grant upstream data rights | Unknown | Unknown | **Not approved** |
| `pbpstats` | NBA, WNBA, and G League play-by-play normalized into possessions, lineups, and shot-zone context | Public Python parser; web retrieval uses NBA sources | Game-oriented cache; NBA identifiers | Parser is open source; upstream data rights remain separate | Unknown | Unknown | **Not approved** |
| PBP Stats API | Derived possession, lineup, on-off, WOWY, and related statistics | Paid subscriber API | Provider API identifiers and request endpoints | Governed by subscription terms not reviewed here | Unknown | Unknown | **Not approved** |
| BALLDONTLIE | Games from 1946-current; free teams, players, and games; paid statistics, box scores, lineups, play-by-play, injuries, odds, and props | API key; free tier 5 requests/minute, paid tiers up to documented limits | Cursor pagination; vendor identifiers; no bulk snapshot contract observed | Unknown until account terms for the intended use are reviewed | Unknown | Vendor exposes odds and props, but permission for NBA Lab use is unknown | **Not approved** |
| SportsDataIO | Commercial scores, statistics, play-by-play, injuries, projections, odds, and historical products | Subscription-specific API and historical products | Vendor identifiers and documented schemas | Determined by purchased contract | Determined by purchased contract | Betting products are separately licensed | **Vendor review required** |
| Sportradar NBA API | Licensed NBA schedules, rosters, statistics, play-by-play, change logs, and real-time feeds | B2B subscription; current NBA API v8 | Vendor UUIDs, schemas, and change-log feeds | Determined by purchased contract | Determined by purchased contract | Separate licensed products and contract terms apply | **Vendor review required** |
| Basketball-Reference / Stathead | Historical player, team, season, and game research | Public pages and paid query product | Page/query oriented; Sports Reference identifiers | Automated collection and reuse are restricted by the data-use policy | Restricted without permission | Unknown | **Reference only** |
| Kaggle NBA datasets | Dataset-specific snapshots with variable season and field coverage | Public index; access and maintenance vary by uploader | Often bulk files with dataset-specific identifiers | Must be established per dataset and upstream source | Must be established per dataset | Must be established per dataset | **Case-by-case only** |

## Approval record required before ingestion

An NBA Lab approval record must identify the exact source and product, approved purpose, terms URL
and review date, attribution, automated retrieval limits, raw retention, correction behavior,
derived-table rights, model-training rights, market-adjacent use, redistribution, and owner approval.
Availability, a package license, an API key, or a successful probe is never sufficient by itself.

## Audit changes

- Removed FiveTimesFive because the site did not respond during the bounded review.
- Removed the Basketball Index YouTube URL because it returned 404.
- Replaced the ambiguous `hoopR-py` label with the maintained `sportsdataverse-py` project.
- Moved source clients and loaders into `APIs & Open Data`; moved Polars and DuckDB into tools.
- Added Sportradar and SportsDataIO as explicitly licensed production-feed candidates.

