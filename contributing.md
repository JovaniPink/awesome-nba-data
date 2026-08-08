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
