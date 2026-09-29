# Jobicy

`https://jobicy.com/api/v2/remote-jobs` with `tag=<keyword>`. Measured: semantic matching, every result remote, median age 4–19 days, almost no overlap with freehire. `jobGeo` lists the allowed countries, which feeds the eligibility check directly. Returns nothing for academic queries.

**Measured 26, 27 and 28 Sept — the same three stale records every time.** Four tags (`product-designer`, `ux-designer`, `design-system`, `product-design`) returned **3 records in total** and none on-discipline: a Staff Android Engineer under `design-system`, and two Canada-only marketing designer roles under `product-design`. `product-designer` and `ux-designer` returned nothing at all. Re-run on 27 and 28 Sept it returned **the identical three rows**, none newer than 20 Sept. It stays in the daily list because it costs one curl per tag, but do not read an empty Jobicy as an empty market, and do not read a changed count as freshness either.
