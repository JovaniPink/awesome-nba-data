# Sports Odds source review — November 2, 2026

Original submission: [@GeminiGeorge22, PR #23](https://github.com/JovaniPink/awesome-nba-data/pull/23). The contributor disclosed ownership of the Actor and AI assistance. Their original commit remains in this branch's ancestry; maintainer corrections are separate and were prepared with AI assistance.

Reviewed the [public Actor page](https://apify.com/publicrecords/sports-odds-api) through a bounded HTTPS request. The publisher documents the `basketball/nba` input path, paid access, main-line and full-board modes, missing-operator reporting and a 12-operator per-run limit for full-board mode. The README drops the numerical brand-count claim, states the full-board limit, and keeps account, snapshot and source-terms boundaries. The original resource creation date remains October 28.

Admission rationale: timestamped market-price observations can support general research and comparison; the entry neither recommends bets nor reproduces picks. Regional operator instances are not described as distinct brands. No open-data or upstream redistribution license is asserted.

Security boundary: review fetched public documentation only. No paid Actor, remote MCP endpoint, account connection, publisher-supplied command or downloaded executable was run. The provider describes default proxy rotation when upstream requests slow down; inclusion is not approval to evade rate limits or access restrictions. Users must assess provider terms and permitted access independently. Authenticated behavior, price accuracy, completeness and third-party service security remain unqualified.

Repository changes are catalog text, metadata, generated projections and this review record. Existing validators and tests are compared with the trusted default branch before execution. No dependency, executable script, workflow, action pin or workflow permission is changed.
