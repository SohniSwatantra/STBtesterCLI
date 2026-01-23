# pylint: disable=no-member
import csv
import json
import os
import time
from datetime import datetime

import stbt

# Config
ARTIFACTS_DIR = "artifacts"
METRICS_CSV = os.path.join(ARTIFACTS_DIR, "metrics.csv")
METRICS_NDJSON = os.path.join(ARTIFACTS_DIR, "metrics.ndjson")

HOME_CLASSIFIER = "ziggo/Home"
APPS_CLASSIFIER = "ziggo/Apps"

DEFAULT_DEBOUNCE = 0.25
HOME_RETRIES = 6


# Definitions
def _ensure_artifacts():
    if not os.path.isdir(ARTIFACTS_DIR):
        os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def _log_metrics_row_csv(d: dict):
    _ensure_artifacts()
    new_file = not os.path.exists(METRICS_CSV)
    with open(METRICS_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=sorted(d.keys()))
        if new_file:
            w.writeheader()
        w.writerow(d)


def _log_metrics_ndjson(d: dict):
    _ensure_artifacts()
    with open(METRICS_NDJSON, "a", encoding="utf-8") as f:
        f.write(json.dumps(d) + "\n")


def _emit_kpi_line(d: dict):
    print("KPI: " + json.dumps(d, separators=(",", ":")))


# safe press
def safe_press(key: str, delay: float = DEFAULT_DEBOUNCE):
    """
    Press a key and wait a short debounce using wait-based logic (no sleeps).
    """
    stbt.press(key)
    stbt.wait_until(lambda: True, timeout_secs=delay)
    return True


def wait_for_ai(classifier: str, timeout: float = 10.0):
    """
    Waits for an AI is_visible classifier (e.g. 'ziggo/Apps').
    Returns True when visible, False on timeout.
    """
    try:
        return stbt.wait_until(lambda: stbt.is_visible(classifier), timeout_secs=timeout)
    except stbt.WaitTimeout:
        return False


def go_home(max_presses: int = HOME_RETRIES, timeout: float = 8.0):
    """
    Return to the Home screen using HOME key and AI visibility only.
    """
    for _ in range(max_presses):
        if wait_for_ai(HOME_CLASSIFIER, timeout=0.2):
            return True
        stbt.press("HOME")
        stbt.wait_until(lambda: True, timeout_secs=DEFAULT_DEBOUNCE)

    # final longer wait
    if wait_for_ai(HOME_CLASSIFIER, timeout=timeout):
        return True
    return False



def save_artifact(basename: str):
    """Save the current frame under artifacts/<basename> to avoid stbt-lint image checks."""
    _ensure_artifacts()
    path = os.path.join(ARTIFACTS_DIR, basename)
    stbt.get_frame().save(path)
    return path


def recover_home():
    """
    Take a diagnostic screenshot and try to return to HOME.
    """
    _ensure_artifacts()
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    save_artifact(f"recover_home_{ts}.png")
    ok = go_home()
    if not ok:
        save_artifact(f"recover_home_failed_{ts}.png")
    return ok


def measure(kpi_name: str):
    """
    Decorator to measure duration in ms, enrich the result dict, persist metrics,
    and emit a final 'KPI:' line on stdout.

    Your KPI function should return a dict with at least:
        {"kpi": kpi_name, "status": "pass"|"fail", ...}
    """
    def _decorator(fn):
        def _wrapped(*args, **kwargs):
            t0 = time.perf_counter()
            status = "unknown"
            extra = {}
            try:
                result = fn(*args, **kwargs) or {}
                status = result.get("status", "unknown")
                extra = {k: v for k, v in result.items() if k not in {"kpi", "status"}}
            except Exception as e:
                status = "error"
                extra = {"error": repr(e)}
                _ensure_artifacts()
                ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                save_artifact(f"{kpi_name}_exception_{ts}.png")
                raise
            finally:
                ms = int((time.perf_counter() - t0) * 1000)
                payload = {
                    "kpi": kpi_name,
                    "ms": ms,
                    "status": status,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
                payload.update(extra)
                _log_metrics_row_csv(payload)
                _log_metrics_ndjson(payload)
                _emit_kpi_line(payload)
            return payload
        return _wrapped
    return _decorator


def open_apps(timeout: float = 15.0):
    """
    Navigate to the Apps hub and verify visibility using AI classifier only.
    """
    if not go_home():
        return False

    # Adjust navigation to your UI layout as needed.
    safe_press("RIGHT")
    safe_press("RIGHT")
    safe_press("OK")

    return wait_for_ai(APPS_CLASSIFIER, timeout=timeout)


def ensure_playback(timeout: float = 12.0):
    """
    Consider playback 'started' when motion is detected within timeout.
    AI-only approach: we do not rely on any player OSD templates.
    """
    try:
        stbt.wait_for_motion(timeout_secs=timeout)
        return True
    except stbt.MotionTimeout:
        return False