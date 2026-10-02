# INTERACTIVE_GUIDE_V1.md

Location: `outputs/interactive/comparative_residential_regulation_index_v1/`

Launch: `python3 -m http.server 8787` from that directory, then open http://localhost:8787/.

Tabs: Start Here, Compare Scenarios, Bridgeport Distribution, Sensitivity, Evidence Explorer,
Excluded Context, Methods and Limits, Download/Audit. See the app's own README.md for full detail.
The app reads only its bundled `data/data.json` (a frozen, reconciled export of the real release-v1
outputs) -- no external network calls, no secrets, no server-side logic.
