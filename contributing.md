# Contribution Guidelines

Please note that this project is released with a [Contributor Code of Conduct](code-of-conduct.md).
By participating, you agree to abide by its terms.

## Suggesting a resource

- Search the README first to avoid duplicates.
- Prefer official documentation, primary sources, maintained projects, and stable canonical URLs.
- Confirm that the resource is active and specifically useful for NBA data, analysis, film study,
  research, or learning.
- Describe what the resource provides, its access level, and any important limitation in one concise
  sentence.
- Identify paid, subscription, archived, model-generated, or unofficial resources accurately.
- Do not submit affiliate or referral links, betting or fantasy picks, generic sports sites, or
  promotional copy.
- Add one resource per pull request when practical, and explain why it improves the list.

## Quality bar

A listed resource should be at least one of the following:

- An authoritative league or provider source.
- A maintained open dataset, API, library, or research tool.
- A distinctive analytical product with clear methodology and general research value.
- A substantive educational source that teaches basketball analytics, film, or data methods.

Descriptions should distinguish observed data, human classifications, model outputs, evaluations,
forecasts, and market data where relevant.

## Validate your change

The catalog gate requires Python 3.11 or newer and has no third-party dependencies:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_readme.py README.md
```

The validator checks structure and formatting only. Before adding or materially updating a resource,
open its canonical source and verify its current maintenance status, access level, relevant license
or terms, and the specific claim made by the description. Include that evidence in the pull request.

## Updating your pull request

If maintainers request changes, update the existing pull request rather than opening a replacement.
If you are unsure how, see this [guide to amending a commit](https://github.com/RichardLitt/knowledge/blob/master/github/amending-a-commit-guide.md).

## Manual external-link audit

Run `python3 scripts/audit_links.py --output /tmp/catalog-link-audit.json` from the
repository root. This standard-library command reads the generated catalog, uses four
workers with 20-second socket timeouts, retries a transient failure once per resource,
and falls back from unsupported, blocked, or missing HEAD responses to GET (at most 64 KiB).
Redirects are limited to five hops. Initial requests, redirects, retries, and GET
fallbacks allow only credential-free HTTPS on port 443 and public IP destinations.

The version 1.1 JSON report includes the input catalog hash, timestamps, resource IDs,
HTTP statuses, redirect chains, final URLs, errors, and all request attempts. A readable
summary is also printed. `reachable` means HTTP success only: the command does not
verify page content, data accuracy, rights, freshness, or completeness. Inspect redirects,
especially changes of host, for unrelated landing pages. Authentication blocks, rate
limits, missing responses, server failures, and transport errors remain separate results.
A 403 or timeout is not evidence that a resource is dead. `security-blocked` means
local policy refused the destination before sending HTTP to it; it is not a publisher
HTTP response. Version 1.1 adds this classification and the destination policy setting;
historical version 1.0 reports remain unchanged.

The connector checks every resolved IPv4/IPv6 address and rejects the entire DNS answer
if any address is non-public. It connects directly to a validated numeric address to
avoid a second DNS lookup, retaining the original hostname for Host, TLS SNI, and
certificate verification. Private, loopback, link-local/metadata, shared, multicast,
reserved, and IPv6 transition/translation destinations are refused. Environment and
system proxies are disabled; there is no insecure bypass option.

This policy intentionally refuses nonstandard ports and some special-purpose ranges.
It is an application-level restriction, not network isolation: DNS still uses the system
resolver, and local routing/firewalls remain outside the tool's control. Run audits in
a restricted environment when processing untrusted catalogs. The tool does not execute
page content or qualify the security of third-party services.

Exit status 0 means a report was written, even if resources need review; status 1 means
invalid input or a failed audit/report write. Supply an existing output directory. This
command never rewrites catalog entries or review dates. It is manual and stays outside
normal CI; its controlled-response tests run offline with the regular unit suite.

See [the October 20 review receipt](docs/catalog-review-2026-10-20.md) for the bounded
content review, contributor attribution, and unresolved source access observations.
