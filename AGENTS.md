# AGENTS.md

## Purpose

This repository is a curated NBA data and analysis catalog. The README is the product; the
validator and hosted workflow protect its structure without pretending to review external sources.

## Canonical commands

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_readme.py README.md
```

The validation code uses only the Python standard library and supports Python 3.11 or newer.

## Catalog contract

- Keep `## Contents` as the first level-two section and in the same order as the catalog sections.
- Do not include `Contributing` or `Footnotes` in Contents.
- Use HTTPS resource URLs.
- Format catalog entries as `- [Name](URL) - Description.` with an uppercase description and a
  terminal period.
- List a canonical resource URL once, in its strongest category.
- Preserve canonical sources and accurately label paid, archived, unofficial, model-generated, and
  license-restricted resources.
- Do not treat a repository-structure review as a catalog-wide source recency review.

## Evidence boundary

A passing validator proves local Markdown structure, anchors, relative links, URL uniqueness, and
entry formatting. It does not prove that an external URL responds, that its content remains high
quality, or that its license and access terms are unchanged. Those claims require source-by-source
review.

## Working rules

- Prefer official documentation, primary sources, and maintained canonical projects.
- Exclude affiliate links, betting picks, fantasy picks, and promotional submissions without a
  distinct general-purpose data or research value.
- Keep deprecated or archived resources in the dedicated legacy section.
- Run both canonical commands before opening or updating a pull request.
- Do not change the repository license without explicit owner approval.
