# Knowledge resource index

`catalog/resources.v1.json` is the public, machine-readable projection of the catalog entries in `README.md`. Each URL receives a stable project-scoped `knowledge-contract.v1` source identifier derived from its canonical URL.

The projection is intentionally conservative. It preserves the catalog name, description, category, and URL, but it does not convert inclusion into endorsement, permission, license, maintenance, availability, or model-fitness evidence. A consuming lab must record its own dated retrieval, exact source snapshot, applicable terms, methodology review, and as-of meaning.

Regenerate and verify the projection with:

```sh
python3 scripts/build_resource_index.py
python3 scripts/build_resource_index.py --check
```

Changing a display name or description preserves the identifier. Changing the canonical URL creates a new identifier so downstream users cannot silently treat a different source location as the same evidence object.
