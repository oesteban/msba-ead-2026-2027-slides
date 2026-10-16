#!/usr/bin/env bash
# Step through a deck with real key presses in headless Chrome and print, for the slide
# on entry and after each press, which .step-N elements (+ shown, - hidden) and which SVG
# data-step layers show. A stepwise slide must open on its first step alone and end with
# everything shown; a screenshot cannot tell you that.
#
#   tools/check-steps.sh day1/02-model 11 4
#
# The second argument is remark's URL hash, which counts the uncounted cover (and About
# me): the slide numbered 11 on screen is #12 in deck 2. Start one slide before the one
# to check: a slide loaded straight from its hash shows every step, as when entered
# backwards. The third argument is how many times to press ArrowRight; the example
# prints #11, then #12 on entry and after each of its steps, then #13.
# puppeteer-core comes from decktape's npx install, the package render-deck.sh fetches.
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
cd "$root"
id="${1:?usage: tools/check-steps.sh <deck-dir> <first slide hash> <presses>}"
first="${2:-1}"
presses="${3:-1}"
chrome="${CHROME:-$(command -v google-chrome || command -v chromium || true)}"
mac="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -n "$chrome" ] || [ ! -x "$mac" ] || chrome="$mac"
[ -n "$chrome" ] || { echo "no Chrome found; set CHROME=/path/to/chrome" >&2; exit 1; }
nm="$(dirname "$(dirname "$(npx --yes -p decktape which decktape)")")"
[ -d "$nm/puppeteer-core" ] || { echo "puppeteer-core not found in $nm" >&2; exit 1; }

port=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')
python3 -m http.server "$port" --bind 127.0.0.1 >/dev/null 2>&1 &
server=$!
trap 'kill $server 2>/dev/null' EXIT
sleep 1

node tools/check-steps.mjs "$nm" "$chrome" "http://127.0.0.1:$port/$id/index.html" "$first" "$presses"
