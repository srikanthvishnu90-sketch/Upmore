#!/usr/bin/env python3
"""Build the full Upmore app: inject upmore-data.json into the template."""
import json, pathlib

HERE = pathlib.Path(__file__).parent
data = json.loads((HERE / "data" / "upmore-data.json").read_text())
tpl = (HERE / "upmore-app-template.html").read_text()
ph = "<!--__UPMORE_DATA__-->"
assert ph in tpl, "placeholder missing from template"

# JSON with </script> escaped so the inline data can't break the page
payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</script>", "<\\/script>")
script = "<script>\nconst UPMORE_DATA = " + payload + ";\n</script>"
out = tpl.replace(ph, script, 1)

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
