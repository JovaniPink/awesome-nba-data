# Awesome NBA Data & Stats [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated list of up-to-date NBA data sources, analytics sites, APIs, tools, and explainers. Each item includes a short description and a reliable URL.

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
- [NBA Top Shot](https://www.nbatopshot.com/) - Official blockchain collectibles; occasionally useful for media assets and moment metadata.

## Analytics & Advanced Metrics Sites

High-signal analytics destinations and dashboards (some paid). Great for impact metrics, lineup analysis, and specialty views.

- [Basketball-Reference](https://www.basketball-reference.com/) - Deep historical database with player/team pages, game logs, and advanced stats.
- [Stathead (Sports-Reference)](https://stathead.com/basketball/) - Powerful paid research queries (player/team/game finders, splits, etc.).
- [ESPN NBA Stats](https://www.espn.com/nba/stats) - League-wide player/team leaderboards and sortable tables.
- [Cleaning the Glass](https://cleaningtheglass.com/) - Subscription analytics that filter out garbage time; rich team, player, lineup views and explainers.
- [Dunks & Threes - EPM](https://dunksandthrees.com/epm) - Public leaderboard for **Estimated Plus-Minus (EPM)** and team ratings; methodology page linked on-site.
- [BBall Index - LEBRON](https://www.bball-index.com/lebron-database/) - Impact metric and tooling (role/skill data, leaderboards, glossary); mix of free and paid.
- [NbaPropLab](https://nbaproplab.com) - AI-powered NBA player props analyzer with a 7-block scoring engine, spider charts, and historical hit-rate tracking.
- [PBP Stats](https://www.pbpstats.com/) - On/Off, WOWY, lineup and possession-based stats; exposes a public API for subscribers.
- [NBAstuffer](https://www.nbastuffer.com/) - Aggregated dashboards, pace/strength-of-schedule, lineup tools, and analytics guides.
- [Inpredictable](http://www.inpredictable.com/) - Win probability models and tempo/variance research for NBA (and other sports).
- [Crafted NBA](https://craftednba.com/) - Player/team dashboards and meta-metrics (DARKO, DRIP, LEBRON, RAPTOR, CraftedPM), comparisons, and roles.
- [NBA RAPM (nbarapm.com)](https://www.nbarapm.com/) - Career and rolling **RAPM** plus cross-metric peak summaries.

## APIs & Open Data

Programmatic access and bulk data for analysis. Mind rate limits and terms of use.

- [nba_api (Python)](https://github.com/swar/nba_api) - Python client for stats.nba.com endpoints (with proper headers/rate limiting handling).
- [PBP Stats API Docs](https://api.pbpstats.com/docs) - Endpoints for possessions, on/off, lineup splits, etc. (subscription).
- [pbpstats (Python)](https://pypi.org/project/pbpstats/) - Library to parse NBA/WNBA/G League play-by-play; powers PBP Stats.
- [balldontlie API](https://www.balldontlie.io/) - Free JSON NBA data API (games, players, stats). Great for prototypes; not 100% complete with tracking/synergy-style data.
- [Basketball Reference Web Scraper (Python)](https://github.com/jaebradley/basketball_reference_web_scraper) - Scrape Basketball-Reference data when API access isn't available.
- [Kaggle - NBA Datasets](https://www.kaggle.com/search?q=NBA+dataset) - Community-maintained season, box score, and play-by-play datasets (quality varies; check provenance).

## YouTube & Learning

- [Thinking Basketball](https://www.youtube.com/ThinkingBasketball) - Film + stats breakdowns, metric explainers, historical series.
- [The Athletic (NBA)](https://www.youtube.com/channel/UCCl9GMgbh3IbMwyMcU3YLjA) - Reporting and analysis.
- [Basketball Index (channel)](https://www.youtube.com/@BasketballIndex) - Occasional metric and player/role breakdowns.
- [Hoops Tonight](https://www.youtube.com/channel/UCw8h_jH2gB20wcZTJiaQNCA) - Analytics, history, and film breakdowns.

## Data Analysis Libraries & Tools

- [nba_api](https://github.com/swar/nba_api) - Official stats client (Python).
- [hoopR (R)](https://hoopR.sportsdataverse.org/) / [hoopR-py (Python)](https://py.sportsdataverse.org/) - SportsDataverse packages for ESPN/NBA data.
- [pbpstats](https://pypi.org/project/pbpstats/) - Possession parsing + lineup/shot zone helpers (Python).

## Advanced Stats Explained

- [PER - Player Efficiency Rating](https://en.wikipedia.org/wiki/Player_efficiency_rating)
- [Win Shares](https://www.basketball-reference.com/about/ws.html)
- [VORP - Value Over Replacement Player](https://en.wikipedia.org/wiki/Value_over_replacement_player)
- [BPM - Box Plus/Minus](https://www.basketball-reference.com/about/bpm2.html)
- [TS% - True Shooting %](https://en.wikipedia.org/wiki/True_shooting_percentage)
- [eFG% - Effective FG%](https://www.breakthroughbasketball.com/stats/effective-field-goal-percentage.html)
- [Net Rating](https://www.bball-index.com/is-net-rating-still-king/)
- [RAPTOR - Intro/Method](https://fivethirtyeight.com/features/introducing-raptor-our-new-metric-for-the-modern-nba/) *(archived explainer; datasets still mirrored various places)*
- [EPM - Estimated Plus-Minus (methodology)](https://dunksandthrees.com/about/epm)
- [LEBRON - Metric Intro](https://www.bball-index.com/lebron-introduction/)

## Legacy / Archived (still useful)

Historical or lower-activity resources - good references, but not always current.

- [DraftExpress](http://www.draftexpress.com/) - Historical scouting archive; DraftExpress now operates within ESPN.
- [82Games](http://www.82games.com/) - Classic lineup/five-man and on/off archives.
- [FiveThirtyEight NBA](https://fivethirtyeight.com/tag/nba/) - NBA coverage largely archived; RAPTOR explainer still valuable.
- [FiveTimesFive](https://fivetimesfive-blog.com/) - Blog: thoughtful analytics write-ups (posting cadence varies).
- [Back Picks](https://backpicks.com/) - Ben Taylor's long-form analytics pieces and historical series.
- [NBA Match Visualizer - Single Game Example](http://nba.papiotis.info/2021-01-22/DETvsHOU) - Example link to a historic game visualization.

---

## Contribute

Spotted a dead link, better mirror, or a new high-signal resource? PRs welcome - keep it clean, current, and non-spammy. See [contributing.md](contributing.md).
