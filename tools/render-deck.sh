#!/usr/bin/env bash
# Render a deck to PDF and to contact sheets, to read the slides back
# (AUTHORING.md F2: compiling is not evidence).
#
#   tools/render-deck.sh day1/02-model -> _preview/day1-02-model.pdf
#                                        _preview/day1-02-model/sheetN.png (12 slides each)
#
# Serves the checkout on a throwaway local port, prints every slide with
# decktape (fetched by npx) in headless Chrome, then tiles the screenshots.
# _preview/ is git-ignored.
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
cd "$root"
id="${1:?usage: tools/render-deck.sh <deck-dir, e.g. day1/02-model>}"
out="_preview/${id//\//-}"
chrome="${CHROME:-$(command -v google-chrome || command -v chromium || true)}"
[ -n "$chrome" ] || { echo "no Chrome found; set CHROME=/path/to/chrome" >&2; exit 1; }

port=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')
python3 -m http.server "$port" --bind 127.0.0.1 >/dev/null 2>&1 &
server=$!
trap 'kill $server 2>/dev/null' EXIT
sleep 1

rm -rf "$out"; mkdir -p "$out/_preview"
# -s is the remark slide's own size (1210x681 at 16:9): at 1280x720 the print
# cuts the right edge of every slide (logo, cover angle, page number).
npx --yes decktape remark --chrome-path "$chrome" --chrome-arg=--no-sandbox -s 1210x681 \
  --screenshots --screenshots-directory "$out" --screenshots-size 640x360 \
  "http://127.0.0.1:$port/$id/index.html" "$out.pdf" 2>&1 | grep -E 'Printed|rror' || true

python3 - "$out" <<'PY'
import glob, re, sys
from PIL import Image
d = sys.argv[1]
fs = sorted(glob.glob(d + "/**/*.png", recursive=True),
            key=lambda f: int(re.search(r"_(\d+)_\d+x\d+", f).group(1)))
ims = [Image.open(f) for f in fs]
for k in range(0, len(ims), 12):
    chunk, cols = ims[k:k + 12], 3
    rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (640 * cols + 20 * (cols - 1), 360 * rows + 20 * (rows - 1)), "#888")
    for i, im in enumerate(chunk):
        sheet.paste(im, ((i % cols) * 660, (i // cols) * 380))
    sheet.save(f"{d}/sheet{k // 12 + 1}.png")
    print(f"{d}/sheet{k // 12 + 1}.png ({len(chunk)} slides)")
PY
