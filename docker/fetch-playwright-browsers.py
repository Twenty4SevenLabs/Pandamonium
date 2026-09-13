#!/usr/bin/env python3
"""Fetch Playwright's pinned Chromium + FFmpeg when nested `node` spawn fails."""
from __future__ import annotations

import io
import os
import pathlib
import sys
import urllib.request
import zipfile

BROWSERS_PATH = pathlib.Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/ms-playwright"))
CHROMIUM = (
    "chromium-1243",
    "https://cdn.playwright.dev/builds/cft/153.0.8010.12/linux64/chrome-linux64.zip",
)
FFMPEG = (
    "ffmpeg-1011",
    "https://cdn.playwright.dev/dbazure/download/playwright/builds/ffmpeg/1011/ffmpeg-linux.zip",
)


def fetch(name: str, url: str) -> None:
    dest = BROWSERS_PATH / name
    dest.mkdir(parents=True, exist_ok=True)
    print(f"fetch-playwright-browsers: downloading {name} from {url}", flush=True)
    with urllib.request.urlopen(url, timeout=300) as response:
        payload = response.read()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        archive.extractall(dest)
    (dest / "INSTALLATION_COMPLETE").write_text("", encoding="utf-8")
    print(f"fetch-playwright-browsers: extracted {name} to {dest}", flush=True)


def main() -> int:
    try:
        fetch(*CHROMIUM)
        fetch(*FFMPEG)
    except Exception as exc:  # noqa: BLE001 — last-resort image build fallback
        print(f"fetch-playwright-browsers: failed: {exc}", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
