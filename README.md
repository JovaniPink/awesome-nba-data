# Awesome NBA Data & Stats [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated list of up-to-date NBA data sources, analytics sites, APIs, tools, and explainers. Each item includes a short description and a reliable URL.

Catalog structure reviewed: August 2026.

External sources are reviewed when they are added or materially changed. A catalog-wide source
recency review has not yet been recorded.

## Contents

- [Official & League Data](#official--league-data)
- [Analytics & Advanced Metrics Sites](#analytics--advanced-metrics-sites)
- [APIs & Open Data](#apis--open-data)
- [YouTube & Learning](#youtube--learning)
- [Data Analysis Libraries & Tools](#data-analysis-libraries--tools)
- [Advanced Stats Explained](#advanced-stats-explained)
- [Legacy / Archived (still useful)](#legacy--archived-still-useful)

---

## Official & League Data

About this section: Official league-operated sites. Best sources for box scores, play-by-play, tracking summaries, rules/officiating and press releases.

- [NBA.com](https://www.nba.com/) - Official league site: scores, news, schedules, standings, and video.
- [NBA Stats (stats.nba.com)](https://www.nba.com/stats/) - Official stats portal (box scores, play-by-play, shooting, tracking summaries, lineups, Hustle, L2M links, etc.).
- [NBA Official (Officiating Hub)](https://official.nba.com/) - Coach's Challenges, Rulebook resources, and the league's public **Last Two Minute** (L2M) reports with call/correctness assessments.
- [NBA Communications](https://pr.nba.com/) - Official press releases: transactions, awards, and league announcements.

## Analytics & Advanced Metrics Sites

High-signal analytics destinations and dashboards (some paid). Great for impact metrics, lineup analysis, and specialty views.

- [Basketball-Reference](https://www.basketball-reference.com/) - Deep historical database with player/team pages, game logs, and advanced stats.
- [Stathead (Sports-Reference)](https://stathead.com/basketball/) - Powerful paid research queries (player/team/game finders, splits, etc.).
- [ESPN NBA Stats](https://www.espn.com/nba/stats) - League-wide player/team leaderboards and sortable tables.
- [Cleaning the Glass](https://cleaningtheglass.com/) - Subscription analytics that filter out garbage time; rich team, player, lineup views and explainers.
- [Dunks & Threes - EPM](https://dunksandthrees.com/epm) - Public leaderboard for **Estimated Plus-Minus (EPM)** and team ratings; methodology page linked on-site.
- [BBall Index - LEBRON](https://www.bball-index.com/lebron-database/) - Impact metric and tooling (role/skill data, leaderboards, glossary); mix of free and paid.
- [PBP Stats](https://www.pbpstats.com/) - On/Off, WOWY, lineup and possession-based stats; exposes a public API for subscribers.
- [NBAstuffer](https://www.nbastuffer.com/) - Aggregated dashboards, pace/strength-of-schedule, lineup tools, and analytics guides.
- [Inpredictable](https://www.inpredictable.com/) - Win probability models and tempo/variance research for NBA and other sports.
- [82Games](https://www.82games.com/) - Lineup, five-player-unit, on/off, physicality, and game-analysis archives with current-season research.
- [Crafted NBA](https://craftednba.com/) - Player/team dashboards and meta-metrics (DARKO, DRIP, LEBRON, RAPTOR, CraftedPM), comparisons, and roles.
- [NBA RAPM (nbarapm.com)](https://www.nbarapm.com/) - Career and rolling **RAPM** plus cross-metric peak summaries.

## APIs & Open Data

Programmatic access and bulk data for analysis. Mind rate limits and terms of use.

- [PBP Stats API Docs](https://api.pbpstats.com/docs) - Endpoints for possessions, on/off, lineup splits, etc. (subscription).
- [balldontlie API](https://www.balldontlie.io/) - Free JSON NBA data API (games, players, stats). Great for prototypes; not 100% complete with tracking/synergy-style data.
- [Kaggle - NBA Datasets](https://www.kaggle.com/search?q=NBA+dataset) - Community-maintained season, box score, and play-by-play datasets (quality varies; check provenance).

## YouTube & Learning

- [Thinking Basketball](https://www.youtube.com/ThinkingBasketball) - Film + stats breakdowns, metric explainers, historical series.
- [The Athletic (NBA)](https://www.youtube.com/channel/UCCl9GMgbh3IbMwyMcU3YLjA) - Reporting and analysis.
- [Basketball Index (channel)](https://www.youtube.com/@BasketballIndex) - Occasional metric and player/role breakdowns.
- [Hoops Tonight](https://www.youtube.com/channel/UCw8h_jH2gB20wcZTJiaQNCA) - Analytics, history, and film breakdowns.

## Data Analysis Libraries & Tools

- [nba_api](https://github.com/swar/nba_api) - Python client for NBA.com statistics endpoints with documented request helpers.
- [hoopR](https://hoopR.sportsdataverse.org/) - R package for loading NBA and other basketball data from SportsDataverse sources.
- [hoopR-py](https://py.sportsdataverse.org/) - Python package for loading basketball data from SportsDataverse sources.
- [pbpstats](https://pypi.org/project/pbpstats/) - Python package for parsing possessions, lineups, and shot zones from NBA, WNBA, and G League play-by-play.
- [Basketball Reference Web Scraper](https://github.com/jaebradley/basketball_reference_web_scraper) - Python package for collecting selected Basketball-Reference data when an API is unavailable.

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
- [FiveTimesFive](https://fivetimesfive-blog.com/) - Blog: thoughtful analytics write-ups (posting cadence varies).
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
resource URLs, and entry formatting. A passing result does not prove that external URLs respond,
that a source is still maintained, or that its access and licensing terms are unchanged; those
require human review.
