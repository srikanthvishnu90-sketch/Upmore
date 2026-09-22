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

dest = HERE / "upmore-app.html"
dest.write_text(out)
print(f"built {dest} ({dest.stat().st_size} bytes)")
