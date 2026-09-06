# Knowledge resource index

`catalog/resources.v1.json` is the public, machine-readable projection of the catalog entries in `README.md`. Each URL receives a stable project-scoped `knowledge-contract.v1` source identifier derived from its canonical URL.

The projection is intentionally conservative. It preserves the catalog name, description, category, and URL, but it does not convert inclusion into endorsement, permission, license, maintenance, availability, or model-fitness evidence. A consuming lab must record its own dated retrieval, exact source snapshot, applicable terms, methodology review, and as-of meaning.

Regenerate and verify the projection with:

```sh
python3 scripts/build_resource_index.py
python3 scripts/build_resource_index.py --check
```

Changing a display name or description preserves the identifier. Changing the canonical URL creates a new identifier so downstream users cannot silently treat a different source location as the same evidence object.

## Source assessments and version compatibility

The projection and its source objects use schemaVersion `1.1`. Access and source authority are
`unknown` because the generator has no reviewed assessment input. Description keywords do not
establish permission, current access or primary-source status; original descriptions remain intact.
The resources.v1.json filename denotes the major projection family and stable URL-derived IDs are
unchanged. Consumers must pin and verify the registry's knowledge-object.v1.1 schema and digest
before accepting these records. A v1.0 consumer must reject v1.1 instead of guessing a default.

The registry schema must be reviewed and promoted before this producer change. This local repair
is not publication, consumer adoption, or a source-by-source rights and availability review.
