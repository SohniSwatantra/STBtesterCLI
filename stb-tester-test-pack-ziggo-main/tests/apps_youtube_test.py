import time
import stbt
from tests.kpi_helpers import (
    measure, safe_press, wait_for_ai, open_apps, recover_home, save_artifact
)

def _navigate_path(keys):
    for key in keys:
        safe_press(key)
    return True

# sanity
def sanity_check():
    """
    Ensure the box is not already on HOME. 
    Strategy: Tune to channel 1, then press HOME.
    """
    safe_press("1")
    safe_press("OK")
    stbt.wait_until(lambda: True, timeout_secs=1.0)
    safe_press("HOME")

# Config app

YOUTUBE_TILE_PATH = ["DOWN"] * 4 + ["RIGHT"] * 6
APPS_ALL_APPS_PATH = ["DOWN"] * 5
YOUTUBE_LANDING_CLASSIFIER = "ziggo/Youtube"

APP_LAUNCH_TIMEOUT = 25.0  # seconds to wait after pressing OK


def _navigate_to_youtube_tile() -> bool:
    """Assumes we're already in the All apps grid. Move focus to the YouTube tile."""
    for key in YOUTUBE_TILE_PATH:
        safe_press(key)
    return True


def _wait_for_landing(timeout: float) -> bool:
    """Wait for the YouTube landing (Welcome back) via AI classifier only."""
    return wait_for_ai(YOUTUBE_LANDING_CLASSIFIER, timeout=timeout)


@measure("app_launch_youtube")
def kpi_app_launch_youtube():
    # Go back to linear channel 1
    sanity_check()
    # 1) Enter Apps hub
    if not open_apps(timeout=15.0):
        save_artifact("youtube_openapps_failed.png")
        recover_home()
        return {"kpi": "app_launch_youtube", "status": "fail", "step": "open_apps"}

    # 2) Enter 'All apps' section (MORE)
    if not _navigate_path(APPS_ALL_APPS_PATH):
        save_artifact("youtube_allapps_nav_failed.png")
        recover_home()
        return {"kpi": "app_launch_youtube", "status": "fail", "step": "navigate_all_apps"}

    # 3) Move to YouTube tile
    if not _navigate_to_youtube_tile():
        save_artifact("youtube_navtile_failed.png")
        recover_home()
        return {"kpi": "app_launch_youtube", "status": "fail", "step": "navigate_tile"}

    # 4) Press OK and start kpi
    t0 = time.perf_counter()
    safe_press("OK")

    # 5) Wait for YouTube Welcome page
    ok = _wait_for_landing(timeout=APP_LAUNCH_TIMEOUT)
    app_ms = int((time.perf_counter() - t0) * 1000)

    if not ok:
        save_artifact("youtube_launch_timeout.png")
        recover_home()
        return {
            "kpi": "app_launch_youtube",
            "status": "fail",
            "step": "wait_landing",
            "app_ms": app_ms,
        }

    return {
        "kpi": "app_launch_youtube",
        "status": "pass",
        "app_ms": app_ms,
    }
