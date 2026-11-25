# Inspection Trail

[Open Inspection Trail](https://coolcode.ca/inspectiontrail/) to search Nova Scotia food-establishment inspection histories, view dated findings with their remedies, and keep a local watchlist. No account or API key is required.

<!-- coolcode:guide -->
Search any establishment name, community or street, or use the province’s current/past-year closure and warning searches. A live lookup opens the official anonymous ASP.NET search session and reads its public results. Report lookups replay that search and retrieve only a returned establishment ID. Broad searches show up to 200 results; refine the query for more precise coverage. Initial examples are explicitly labelled starter captures, with their original source upload and retrieval dates.

Each report retains the province’s inspection dates, status wording, findings and required remedies. Boil-water advisory issue and removal dates are displayed separately. A historical “Deficient” entry does not mean that finding remains unresolved today; no hygiene score, safety rating or present-day health conclusion is inferred. Read the original source and its definitions when interpreting a report.

“Watch establishment” saves its name, address and reproducible search on this device. It survives ordinary browser refreshes, but does not automatically check for changes, send alerts or sync. A saved search can be rerun at any time; a dated report can be downloaded as text. Search inputs leave the browser for CoolCode’s public API and the provincial source; watchlists stay in this browser. Provincial detail URLs require a source session, so the tool links to the official search and explains how to reproduce the result.
<!-- /coolcode:guide -->

## Public source and limitations

- [Nova Scotia Food Establishment Inspection Reports](https://www.novascotia.ca/food-establishment-inspection-reports)
- [Official search](https://novascotia.ca/nse/food-protection/reports/Request.aspx)
- [Official inspection status definitions](https://novascotia.ca/nse/food-protection/reports/definitions.aspx)

The province says reports are normally available within three days. Its search upload timestamp is shown as `source_updated`; the collection/API retrieval timestamp is separate. Findings and remedies are preserved as text; whitespace is normalized. No deficiency is silently omitted if the source layout changes. Empty findings tables with the province’s explicit no-deficiency statement are legitimate, and dated inspection entries remain visible.

Source: Nova Scotia Environment and Climate Change. Crown copyright, Province of Nova Scotia. This is an independent presentation, not an official service or endorsement. The province advises that original inspection reports take precedence over website discrepancies. The public report website does not advertise a JSON API. It is adapted through a bounded, read-only form submission.

On the initial check, the province’s **Current Warnings** form returned its “Unknown Error” page. This tool reports a source failure and links to the official search; it never substitutes a zero-warning claim. Other source errors likewise preserve the previous results/capture. Current closures are a dated search category, not a claim that an old starter capture describes today’s operations.

## API adapter

Worker base: `https://coolcode-visitor-api.jeffdyer.workers.dev`.

- `GET /api/inspectiontrail/search?q=NAME&town=COMMUNITY&address=STREET&mode=search`
- `GET /api/inspectiontrail/report?q=NAME&town=COMMUNITY&id=RETURNED_ID&mode=search`
- Modes: `search`, `current-closures`, `closures-year`, `current-warnings`, `warnings-year`.

At least one ordinary search field must contain two characters. Inputs are bounded, unknown/repeated parameters rejected. No arbitrary source URL or caller cookies are accepted. Search is at most two source requests; detail is at most three; each body is limited to 2MB and the chain to 30 seconds. Anonymous source cookies are kept only inside that request chain. The existing Worker D1 cache/client limiter/shared budget provides a five-minute cache and a 1,500-request daily source allowance. The Worker returns `{fetched_at,data}` or its standard non-2xx error envelope.

The maintained helper is [inspection-gateway.js in the hub](https://github.com/jsdyer/jsdyer.github.io/blob/main/services/cloudflare-visitor/inspection-gateway.js). Its parser matches `web/source.mjs`. Update and test both when the source changes. The generated Worker must be deployed after adapter changes; adding a repo ID alone does not deploy the live search implementation. There are no new secrets or bindings.

## Expand or customize

1. Edit `web/config.json` `starter_queries` to add any name/community/street search or supported report category. Each entry has a label, query fields, mode and `capture_reports` limit. These starter searches do not constrain the visitor’s live input. `api_base` and `official_search` describe the infrastructure and official fallback.
2. Run `python3 scripts/refresh.py`. It fetches each search in a fresh anonymous session, retrieves the configured report count and normalizes through `scripts/normalize.mjs` / `web/source.mjs`. Inspect the result dates and counts. A failed source or unrecognized report prevents replacement of the previous capture.
3. Run the tests/build below, then publish the main branch via GitHub Actions Pages. `dist/` is generated and must not be committed. Content-versioned assets ensure a returning browser loads the current application and committed capture.
4. To add another jurisdiction, implement and test a source-specific adapter with its own terms, dates and definitions. Do not silently treat another province’s labels as Nova Scotia’s meanings.

Earlier validated captures remain in Git history. Existing captures with different query coverage are rendered from their own data, counts and dates; presets are not used as an authoritative inventory. A downloaded dated report remains a historical record when a later capture is published.

## Tests and local use

```sh
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py
python3 -m http.server --directory dist 8000
python3 -m pip install -r tests/browser-requirements.txt
CHROMIUM_PATH=/usr/bin/google-chrome python3 tests/browser_smoke.py
```

Builds are offline; collection uses only Python and Node standard libraries. Tests cover exact dated findings/remedies, advisory removals, clean inspections, unexpected layouts, arbitrary search terms, watchlist persistence, source-error handling and narrow/mobile layouts. The hub’s separate gateway tests cover sessions, trusted hosts, input validation and report membership.

## Operations

`.github/workflows/pages.yml` runs at **09:31 UTC daily**, on main changes and manual dispatch. Collection step: **Refresh official inspection starter captures**. The separate schedule guard allowlists `pages.yml` and itself. Small probe `https://coolcode.ca/inspectiontrail/data/status.json` has `checked_at` (successful full configured capture, 36-hour tolerance) and `record_count` (captured full establishment reports, not all establishments or inspections). No dispatch inputs or API keys are required. Grant the independent watchdog’s existing GitHub App access to this repo and register that collector and probe centrally.

Follow the [CoolCode lifecycle](https://github.com/jsdyer/jsdyer.github.io/blob/main/docs/tool-lifecycle.md) for catalogue, guide, sitemap, repository audit, Worker deployment and watchdog integration.
