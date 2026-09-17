#!/usr/bin/env python3
"""Capture an already running, local Streamlit app. Refuses database-error pages."""
import argparse
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--url",default="http://127.0.0.1:8501")
args=parser.parse_args()
if urlparse(args.url).hostname not in {"127.0.0.1","localhost"}:
    raise SystemExit("This helper only captures the local application. Do not capture real personal records without permission.")
out=Path(__file__).resolve().parents[1]/"docs/screenshots/runtime"
out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport={"width":1440,"height":1080},device_scale_factor=1)
    for route,name in [("/","dashboard"),("/students","students"),("/courses","courses"),("/grades","grades"),("/reports","reports"),("/terms","terms"),("/privacy","privacy")]:
        page.goto(args.url.rstrip("/")+route,wait_until="domcontentloaded")
        page.locator(".cb-page-heading").wait_for(timeout=30000)
        page.locator(".cb-footer").wait_for(timeout=30000)
        if page.get_by_text("No data is shown from a fallback database.",exact=False).count():
            raise RuntimeError("The page reports a database error; refusing to create misleading screenshots.")
        if page.locator('[data-testid="stException"]').count():
            raise RuntimeError("Streamlit reported an exception; fix it before capturing screenshots.")
        page.screenshot(path=str(out/f"{name}.png"),full_page=True)
        print(out/f"{name}.png")
    browser.close()
