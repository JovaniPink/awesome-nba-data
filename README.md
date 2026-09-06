# Awesome NBA Data & Stats [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated list of up-to-date NBA data sources, analytics sites, APIs, tools, and explainers. Each item includes a short description and a reliable URL.

Catalog structure reviewed: August 2026.

Catalog entries present on August 13, 2026, were reviewed on that date. Later additions carry
their own `reviewed_at` dates in the dated [source audit](docs/source-audit.tsv), which records URL
behavior and access classification. The [source matrix](docs/source-matrix.md) keeps programmatic
coverage and use constraints separate from link availability. A responding URL is not permission
to collect, store, model, or republish its data.

The [machine-readable resource index](catalog/resources.v1.json) assigns stable public identifiers while preserving the catalog boundary: inclusion is curation, not endorsement, permission, maintenance proof, or model fitness proof. The index uses schema version 1.1 and retains unknown access and source authority until reviewed evidence is supplied. See the [resource index contract](docs/knowledge-resource-index.md) before using an entry in a model or lab.

## Contents

- [Official & League Data](#official--league-data)
- [Analytics & Advanced Metrics Sites](#analytics--advanced-metrics-sites)
- [APIs & Open Data](#apis--open-data)
- [Licensed Production Feeds](#licensed-production-feeds)
- [YouTube & Learning](#youtube--learning)
- [Data Analysis Libraries & Tools](#data-analysis-libraries--tools)
- [Advanced Stats Explained](#advanced-stats-explained)
- [Legacy / Archived (still useful)](#legacy--archived-still-useful)

---

## Official & League Data

About this section: Official league-operated sites. Best sources for box scores, play-by-play, tracking summaries, rules/officiating and press releases.

- [NBA.com](https://www.nba.com/) - Official league site for scores, schedules, standings, news, and video; use remains subject to NBA terms.
- [NBA Stats (stats.nba.com)](https://www.nba.com/stats/) - Official stats portal for box scores, play-by-play, shooting, tracking summaries, lineups, and Hustle data; it is not a published bulk-data license.
- [NBA Official (Officiating Hub)](https://official.nba.com/) - Official rulebook, Coach's Challenge, and Last Two Minute report hub.
- [NBA Communications](https://pr.nba.com/) - Official press releases for transactions, awards, schedule changes, and league announcements.
- [NBA Injury Report: 2025-26 Season](https://official.nba.com/nba-injury-report-2025-26-season/) - Official, season-specific reports containing participation statuses and stated reasons that teams update throughout reporting windows; this changing web reference is not a historical bulk-data API.
- [NBA Player Transactions](https://www.nba.com/players/transactions) - Official filterable transaction reference for signings, waivers, trades, and other roster moves; the public page does not establish a documented bulk-data license.

## Analytics & Advanced Metrics Sites

High-signal analytics destinations and dashboards (some paid). Great for impact metrics, lineup analysis, and specialty views.

- [Basketball-Reference](https://www.basketball-reference.com/) - Unofficial historical reference for player, team, season, and game pages; automated reuse is governed by Sports Reference's data-use policy.
- [Stathead (Sports-Reference)](https://stathead.com/basketball/) - Paid research queries for player, team, game, streak, and split analysis.
- [ESPN NBA Stats](https://www.espn.com/nba/stats) - Unofficial league-wide player and team leaderboards with sortable tables.
- [Cleaning the Glass](https://cleaningtheglass.com/) - Paid analytics that filter garbage time and provide team, player, and lineup views.
- [Dunks & Threes - EPM](https://dunksandthrees.com/epm) - Derived Estimated Plus-Minus and team-rating leaderboards with a public methodology page.
- [BBall Index - LEBRON](https://www.bball-index.com/lebron-database/) - Derived role, skill, and LEBRON tooling with a mix of public and paid access.
- [PBP Stats](https://www.pbpstats.com/) - Derived on-off, WOWY, lineup, and possession views with a subscriber API.
- [NBAstuffer](https://www.nbastuffer.com/) - Aggregated dashboards, pace/strength-of-schedule, lineup tools, and analytics guides.
- [Inpredictable](https://www.inpredictable.com/) - Win probability models and tempo/variance research for NBA and other sports.
- [82Games](https://www.82games.com/) - Lineup, five-player-unit, on/off, physicality, and game-analysis archives with current-season research.
- [Crafted NBA](https://craftednba.com/) - Player/team dashboards and meta-metrics (DARKO, DRIP, LEBRON, RAPTOR, CraftedPM), comparisons, and roles.
- [NBA RAPM (nbarapm.com)](https://www.nbarapm.com/) - Career and rolling **RAPM** plus cross-metric peak summaries.

## APIs & Open Data

Programmatic discovery and research tools. An open client or reachable endpoint does not grant
rights to the upstream data.

- [nba_api](https://github.com/swar/nba_api) - Unofficial MIT-licensed Python client for NBA.com endpoints; upstream schemas and endpoints change without a public stability contract.
- [hoopR](https://hoopr.sportsdataverse.org/) - Open-source R package and bulk loaders for men's basketball data, including NBA play-by-play releases from 2002 onward.
- [sportsdataverse-py](https://py.sportsdataverse.org/) - Open-source Python package for NBA schedules, play-by-play, box scores, rosters, and related source wrappers.
- [pbpstats](https://github.com/dblackrun/pbpstats) - Open-source parser that derives possessions, lineups, and shot-zone context from NBA, WNBA, and G League play-by-play.
- [PBP Stats API Docs](https://api.pbpstats.com/docs) - Paid API documentation for derived possession, lineup, on-off, and WOWY data.
- [BALLDONTLIE NBA API](https://docs.balldontlie.io/) - API-key service with free teams, players, and games; statistics, play-by-play, lineups, injuries, and odds require paid tiers.
- [Kaggle - NBA Datasets](https://www.kaggle.com/search?q=NBA+dataset) - Community dataset index where provenance, license, coverage, and correction behavior must be checked per dataset.

## Licensed Production Feeds

Commercial feeds whose contract, purchased products, and approved purpose determine permitted use.

- [Sportradar NBA API](https://developer.sportradar.com/basketball/docs/nba-ig-api-basics) - Licensed B2B NBA feeds with schedules, rosters, statistics, play-by-play, change logs, and provider identifiers.
- [SportsDataIO NBA API](https://sportsdata.io/developers/api-documentation/nba) - Commercial NBA feeds for scores, statistics, play-by-play, injuries, projections, and betting data with subscription-specific access.

## YouTube & Learning

- [Thinking Basketball](https://www.youtube.com/ThinkingBasketball) - Film + stats breakdowns, metric explainers, historical series.
- [The Athletic (NBA)](https://www.youtube.com/channel/UCCl9GMgbh3IbMwyMcU3YLjA) - Reporting and analysis.
- [Hoops Tonight](https://www.youtube.com/channel/UCw8h_jH2gB20wcZTJiaQNCA) - Analytics, history, and film breakdowns.

## Data Analysis Libraries & Tools

- [Polars](https://pola.rs/) - Open-source DataFrame engine suited to typed, lazy transformations over Parquet and other analytical formats.
- [DuckDB](https://duckdb.org/) - Open-source analytical database for local SQL over Parquet and reproducible research snapshots.
- [Basketball Reference Web Scraper](https://github.com/jaebradley/basketball_reference_web_scraper) - Unofficial Python scraper retained for legacy research; Sports Reference policy review is required before automated use.

## Advanced Stats Explained

- [PER - Player Efficiency Rating](https://en.wikipedia.org/wiki/Player_efficiency_rating) - Overview of John Hollinger's pace-adjusted box-score summary metric.
- [Win Shares](https://www.basketball-reference.com/about/ws.html) - Basketball-Reference methodology for allocating estimated team wins to players.
- [VORP - Value Over Replacement Player](https://en.wikipedia.org/wiki/Value_over_replacement_player) - Overview of the box-score estimate of points contributed relative to a replacement player.
- [BPM - Box Plus/Minus](https://www.basketball-reference.com/about/bpm2.html) - Basketball-Reference methodology for estimating player contribution per 100 possessions from box-score data.
- [TS% - True Shooting Percentage](https://en.wikipedia.org/wiki/True_shooting_percentage) - Overview of scoring efficiency that incorporates field goals, three-pointers, and free throws.
- [eFG% - Effective Field Goal Percentage](https://www.breakthroughbasketball.com/stats/effective-field-goal-percentage.html) - Explanation of field-goal percentage adjusted for the added value of three-pointers.
- [Net Rating](https://www.bball-index.com/is-net-rating-still-king/) - Discussion of team or lineup point differential per 100 possessions and its limitations.
- [RAPTOR - Intro and Method](https://fivethirtyeight.com/features/introducing-raptor-our-new-metric-for-the-modern-nba/) - Archived FiveThirtyEight explainer for its historical player-impact model.
- [EPM - Estimated Plus-Minus Methodology](https://dunksandthrees.com/about/epm) - Dunks & Threes methodology for its player-impact estimate.
- [LEBRON - Metric Introduction](https://www.bball-index.com/lebron-introduction/) - Basketball Index introduction to its player-impact metric and design goals.

## Legacy / Archived (still useful)

Historical or lower-activity resources - good references, but not always current.

- [FiveThirtyEight NBA](https://fivethirtyeight.com/tag/nba/) - NBA coverage largely archived; RAPTOR explainer still valuable.
- [Back Picks](https://backpicks.com/) - Ben Taylor's long-form analytics pieces and historical series.

---

## Contributing

Spotted a dead link, better mirror, or a new high-signal resource? Pull requests are welcome. Keep
additions current, specific, and non-promotional; see [contributing.md](contributing.md).

Before opening a pull request, run the dependency-free catalog gate with Python 3.11 or newer:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_readme.py README.md
```

GitHub Actions runs the same checks on Python 3.11 and Python 3.14 for every pull request and push to
`main`. The validator checks Contents order and anchors, required files, relative links, unique HTTPS
resource URLs, entry formatting, and exact coverage in the dated source audit. A passing result does
not prove permission, maintenance quality, or fit for a particular use; those require the source
matrix and an explicit terms review.
