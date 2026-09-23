#!/usr/bin/env python3
"""Build the full Upmore app: inject upmore-data.json into the template."""
import json, pathlib

HERE = pathlib.Path(__file__).parent
data = json.loads((HERE / "data" / "upmore-data.json").read_text())
tpl = (HERE / "upmore-app-template.html").read_text()
ph = "<!--__UPMORE_DATA__-->"
assert ph in tpl, "placeholder missing from template"

# Owner direction 2026-09-23: credit cards are out of the product entirely —
# drop retired credit-card routes from the served bundle (they stay in the
# source JSON + DB as retired for audit).
CC_CATS = {"Credit Card Bonus", "Card Bonus"}
data["routes"] = [r for r in data.get("routes", [])
                  if not (r.get("status") == "retired" and r.get("category") in CC_CATS)]

# JSON with </script> escaped so the inline data can't break the page
payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</script>", "<\\/script>")
script = "<script>\nconst UPMORE_DATA = " + payload + ";\n</script>"
out = tpl.replace(ph, script, 1)

# Keep the hardcoded marketing/copy counts in sync with the real data
n_routes = len(data.get("routes", []))
n_verified = sum(1 for r in data.get("routes", []) if r.get("status") == "verified")
n_steps = sum(len(r.get("steps") or []) for r in data.get("routes", []))
out = out.replace("Search 535 ways to earn…", f"Search {n_routes} ways to earn…")
out = out.replace("(535 routes, 4,953 playbook", f"({n_routes} routes, {n_steps:,} playbook")
out = out.replace("I can look up any of the 535 routes in the catalog",
                  f"I can look up any of the {n_routes} routes in the catalog")
out = out.replace("the real 535-route catalog", f"the real {n_routes}-route catalog")
out = out.replace('"Rebate/Incentive":"tag"',
                  '"Rebate/Incentive":"tag", "Credit Card Bonus":"card"')
assert "535" not in out.split("const UPMORE_DATA")[0], "stale 535 count remains in template copy"

# Vendor supabase-js inline so the app has zero external script dependencies
js_ph = "<!--__SUPABASE_JS__-->"
assert js_ph in out, "supabase placeholder missing from template"
vendor = (HERE / "vendor" / "supabase-js.min.js").read_text()
assert "createClient" in vendor, "vendored supabase-js looks wrong"
out = out.replace(js_ph, "<script>\n" + vendor + "\n</script>", 1)

dest = HERE / "upmore-app.html"
dest.write_text(out)
print(f"built {dest} ({dest.stat().st_size} bytes)")

# Publish to repo root for Vercel: index.html + sw.js
root = HERE.parent
(root / "index.html").write_text(out)
print(f"published {root / 'index.html'}")
sw_src = HERE / "sw.js"
if sw_src.exists():
    (root / "sw.js").write_text(sw_src.read_text())
    print(f"published {root / 'sw.js'}")
