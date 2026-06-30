# Release 1.0.13

`1.0.13` fixes adapter-health dashboard card markup so consumer dashboards keep
compact, predictable card layout even when adapter titles and sparkline buckets
both link to consumer-owned routes.

## Changes

- Render adapter cards as `<article>` elements with a linked title instead of
  wrapping the entire card in a link.
- Preserve per-bucket sparkline links without creating nested anchors.
- Tighten adapter-card grid sizing so health cards stay compact and aligned in
  dense operator dashboards.
- Extend adapter-health tests to cover linked titles, linked sparkline buckets,
  and escaped runtime-provided URLs.

## Consumer Notes

Consumers do not need to change their adapter-health data shape. Existing
`href` values on adapter cards continue to render as title links, and existing
sparkline bucket `href` values remain clickable. Route ownership, auth, and raw
runtime data remain consumer-owned.

## Verification

```bash
PYTHONPATH=src python -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.13
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.13.html
python3 -m compileall -q src tests examples
```
