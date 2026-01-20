#!/usr/bin/env python3
"""
STB Tester MCP Server

A Model Context Protocol server that exposes STB Tester APIs as tools.
This allows Claude Code and other MCP clients to control set-top boxes
and perform automated testing.

Supports:
- Local stbt_core operations (when running on STB Tester hardware)
- Remote device control via STB Tester Portal API

Environment Variables:
    STBT_PORTAL_URL: STB Tester Portal URL (e.g., https://company.stb-tester.com)
    STBT_PORTAL_TOKEN: API authentication token

Usage:
    python stb_tester_server.py

Or install and run via MCP configuration.
"""

import asyncio
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from typing import Any, Optional

# Add parent directory to path for stbt_core import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
    )
except ImportError:
    print("MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# STB Tester imports - wrapped in try/except for flexibility
try:
    import stbt_core as stbt
    STBT_AVAILABLE = True
except ImportError:
    STBT_AVAILABLE = False
    print("Warning: stbt_core not available. Running in mock mode.", file=sys.stderr)


# Portal API Configuration
PORTAL_URL = os.environ.get("STBT_PORTAL_URL", "")
PORTAL_TOKEN = os.environ.get("STBT_PORTAL_TOKEN", "")
PORTAL_AVAILABLE = bool(PORTAL_URL and PORTAL_TOKEN)

if PORTAL_AVAILABLE:
    print(f"Portal API configured: {PORTAL_URL}", file=sys.stderr)
else:
    print("Portal API not configured. Set STBT_PORTAL_URL and STBT_PORTAL_TOKEN for remote device access.", file=sys.stderr)


# Create the MCP server
server = Server("stb-tester")

# Track connected device
connected_device: Optional[str] = None


class PortalClient:
    """Client for STB Tester Portal REST API."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make an authenticated request to the Portal API."""
        url = f"{self.base_url}/api/v2{endpoint}"
        headers = {
            "Authorization": f"token {self.token}",
            "Content-Type": "application/json",
        }

        req_data = json.dumps(data).encode() if data else None
        request = urllib.request.Request(url, data=req_data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status == 204:
                    return {"status": "success"}
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else str(e)
            return {"error": f"HTTP {e.code}: {error_body}"}
        except urllib.error.URLError as e:
            return {"error": f"Connection error: {e.reason}"}

    def _request_binary(self, endpoint: str) -> tuple[bytes, str]:
        """Make a request that returns binary data (e.g., screenshot)."""
        url = f"{self.base_url}/api/v2{endpoint}"
        headers = {
            "Authorization": f"token {self.token}",
        }
        request = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                content_type = response.headers.get("Content-Type", "image/png")
                return response.read(), content_type
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTP {e.code}: {e.read().decode() if e.fp else str(e)}")

    def list_nodes(self) -> dict:
        """List all available STB Tester nodes."""
        return self._request("GET", "/nodes")

    def get_node(self, node_id: str) -> dict:
        """Get details for a specific node."""
        return self._request("GET", f"/nodes/{node_id}")

    def get_screenshot(self, node_id: str) -> tuple[bytes, str]:
        """Capture a screenshot from a node."""
        return self._request_binary(f"/nodes/{node_id}/screenshot.png")

    def press_key(self, node_id: str, key: str) -> dict:
        """Send a key press to a node."""
        return self._request("POST", f"/nodes/{node_id}/press", {"key": key})

    def run_test(self, node_id: str, test_pack: str, test_case: str, **kwargs) -> dict:
        """Run a test on a node."""
        data = {
            "test_pack": test_pack,
            "test_case": test_case,
            **kwargs
        }
        return self._request("POST", f"/nodes/{node_id}/run", data)

    def get_job_status(self, job_id: str) -> dict:
        """Get the status of a running job."""
        return self._request("GET", f"/jobs/{job_id}")


# Initialize portal client if configured
portal_client: Optional[PortalClient] = None
if PORTAL_AVAILABLE:
    portal_client = PortalClient(PORTAL_URL, PORTAL_TOKEN)


# Mock implementations for when stbt is not available
class MockStbt:
    """Mock STB Tester for testing without hardware."""

    class Region:
        def __init__(self, x=0, y=0, width=1920, height=1080):
            self.x = x
            self.y = y
            self.width = width
            self.height = height

        def __repr__(self):
            return f"Region(x={self.x}, y={self.y}, width={self.width}, height={self.height})"

    class MatchResult:
        def __init__(self, match=True):
            self.match = match
            self.position = MockStbt.Region(100, 100, 50, 50)
            self.first_pass_result = 0.95

    @staticmethod
    def press(key):
        return {"status": "success", "key": key, "mode": "mock"}

    @staticmethod
    def press_and_wait(key, stable_secs=1):
        return {"status": "success", "key": key, "stable_secs": stable_secs, "mode": "mock"}

    @staticmethod
    def match(image, region=None):
        return MockStbt.MatchResult(match=True)

    @staticmethod
    def wait_for_match(image, timeout_secs=10, region=None):
        return MockStbt.MatchResult(match=True)

    @staticmethod
    def wait_for_motion(timeout_secs=5, region=None):
        return {"motion_detected": True, "mode": "mock"}

    @staticmethod
    def ocr(region=None, mode=None):
        return "Mock OCR Text"

    @staticmethod
    def get_frame():
        # Return a minimal valid image bytes (1x1 black PNG)
        return None

    @staticmethod
    def press_until_match(key, image, max_presses=10, interval_secs=1):
        return MockStbt.MatchResult(match=True)


# Use real stbt or mock
stbt_impl = stbt if STBT_AVAILABLE else MockStbt()


def region_from_dict(region_dict: Optional[dict]) -> Optional[Any]:
    """Convert a dictionary to an stbt.Region object."""
    if region_dict is None:
        return None
    if STBT_AVAILABLE:
        return stbt.Region(
            x=region_dict.get("x", 0),
            y=region_dict.get("y", 0),
            width=region_dict.get("width", 1920),
            height=region_dict.get("height", 1080)
        )
    return MockStbt.Region(**region_dict)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available STB Tester tools."""
    tools = [
        # === Portal/Remote Device Tools ===
        Tool(
            name="stb_list_devices",
            description="List all available STB Tester nodes/devices. Requires Portal API configuration (STBT_PORTAL_URL and STBT_PORTAL_TOKEN environment variables).",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="stb_connect_device",
            description="Connect to a specific STB Tester node by device ID. This sets the active device for subsequent operations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The node/device ID to connect to (e.g., 'stb-tester-node-001')"
                    }
                },
                "required": ["device_id"]
            }
        ),
        Tool(
            name="stb_device_info",
            description="Get detailed information about the currently connected device or a specific device.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device ID (optional, uses connected device if not specified)"
                    }
                }
            }
        ),
        Tool(
            name="stb_device_screenshot",
            description="Capture a screenshot from the connected remote device. Returns the image for visual analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device ID (optional, uses connected device if not specified)"
                    },
                    "save_path": {
                        "type": "string",
                        "description": "Optional local path to save the screenshot"
                    }
                }
            }
        ),
        Tool(
            name="stb_device_press",
            description="Send a key press to the connected remote device. Common keys: KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_OK, KEY_BACK, KEY_HOME, KEY_EPG, KEY_PLAY, KEY_PAUSE",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The remote control key to press"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "Device ID (optional, uses connected device if not specified)"
                    }
                },
                "required": ["key"]
            }
        ),
        Tool(
            name="stb_run_test",
            description="Run a test script on a remote STB Tester node.",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_pack": {
                        "type": "string",
                        "description": "The test pack containing the test (e.g., 'my-tests')"
                    },
                    "test_case": {
                        "type": "string",
                        "description": "The test case to run (e.g., 'tests/test_epg.py::test_open_guide')"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "Device ID (optional, uses connected device if not specified)"
                    }
                },
                "required": ["test_pack", "test_case"]
            }
        ),
        Tool(
            name="stb_job_status",
            description="Get the status of a running test job.",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "The job ID returned when starting a test"
                    }
                },
                "required": ["job_id"]
            }
        ),
        # === Local STB Tester Tools ===
        Tool(
            name="stb_press",
            description="Press a remote control key on the set-top box. Common keys: KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_OK, KEY_BACK, KEY_HOME, KEY_EPG, KEY_PLAY, KEY_PAUSE, KEY_STOP, KEY_FASTFORWARD, KEY_REWIND, KEY_0 through KEY_9, KEY_RED, KEY_GREEN, KEY_YELLOW, KEY_BLUE",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The remote control key to press (e.g., KEY_OK, KEY_UP, KEY_EPG)"
                    }
                },
                "required": ["key"]
            }
        ),
        Tool(
            name="stb_press_and_wait",
            description="Press a key and wait for the screen to stabilize. Useful when navigation causes screen transitions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The remote control key to press"
                    },
                    "stable_secs": {
                        "type": "number",
                        "description": "Seconds to wait for screen stability (default: 1)",
                        "default": 1
                    }
                },
                "required": ["key"]
            }
        ),
        Tool(
            name="stb_press_until_match",
            description="Press a key repeatedly until a target image appears on screen. Useful for navigating lists or menus.",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The key to press repeatedly (e.g., KEY_DOWN)"
                    },
                    "image": {
                        "type": "string",
                        "description": "Path to the reference image to match"
                    },
                    "max_presses": {
                        "type": "integer",
                        "description": "Maximum number of key presses (default: 10)",
                        "default": 10
                    },
                    "interval_secs": {
                        "type": "number",
                        "description": "Seconds between presses (default: 1)",
                        "default": 1
                    }
                },
                "required": ["key", "image"]
            }
        ),
        Tool(
            name="stb_match",
            description="Check if a reference image is currently visible on screen. Returns match result with confidence score.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image": {
                        "type": "string",
                        "description": "Path to the reference image file"
                    },
                    "region": {
                        "type": "object",
                        "description": "Optional screen region to search in",
                        "properties": {
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "width": {"type": "integer"},
                            "height": {"type": "integer"}
                        }
                    }
                },
                "required": ["image"]
            }
        ),
        Tool(
            name="stb_wait_for_match",
            description="Wait for a reference image to appear on screen. Raises timeout if image not found.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image": {
                        "type": "string",
                        "description": "Path to the reference image file"
                    },
                    "timeout_secs": {
                        "type": "number",
                        "description": "Maximum seconds to wait (default: 10)",
                        "default": 10
                    },
                    "region": {
                        "type": "object",
                        "description": "Optional screen region to search in",
                        "properties": {
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "width": {"type": "integer"},
                            "height": {"type": "integer"}
                        }
                    }
                },
                "required": ["image"]
            }
        ),
        Tool(
            name="stb_wait_for_motion",
            description="Wait for motion/video playback on screen. Useful for verifying video is playing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeout_secs": {
                        "type": "number",
                        "description": "Maximum seconds to wait for motion (default: 5)",
                        "default": 5
                    },
                    "region": {
                        "type": "object",
                        "description": "Optional screen region to check for motion",
                        "properties": {
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "width": {"type": "integer"},
                            "height": {"type": "integer"}
                        }
                    }
                }
            }
        ),
        Tool(
            name="stb_ocr",
            description="Read text from the screen using OCR (Optical Character Recognition).",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "object",
                        "description": "Screen region to read text from (required for accuracy)",
                        "properties": {
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "width": {"type": "integer"},
                            "height": {"type": "integer"}
                        }
                    },
                    "mode": {
                        "type": "string",
                        "description": "OCR mode: PAGE, SINGLE_LINE, SINGLE_WORD, or SINGLE_CHAR",
                        "enum": ["PAGE", "SINGLE_LINE", "SINGLE_WORD", "SINGLE_CHAR"]
                    }
                }
            }
        ),
        Tool(
            name="stb_screenshot",
            description="Capture a screenshot from the current video frame. Returns base64-encoded PNG image.",
            inputSchema={
                "type": "object",
                "properties": {
                    "save_path": {
                        "type": "string",
                        "description": "Optional path to save the screenshot file"
                    }
                }
            }
        ),
        Tool(
            name="stb_get_config",
            description="Get the current STB Tester configuration values.",
            inputSchema={
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "description": "Config section (e.g., 'global', 'match', 'ocr')"
                    },
                    "key": {
                        "type": "string",
                        "description": "Config key within the section"
                    }
                }
            }
        ),
        Tool(
            name="stb_navigate_menu",
            description="Navigate through a menu using directional keys to reach a target item (identified by image or text).",
            inputSchema={
                "type": "object",
                "properties": {
                    "target_image": {
                        "type": "string",
                        "description": "Path to reference image of target menu item"
                    },
                    "target_text": {
                        "type": "string",
                        "description": "Text to find via OCR (alternative to image)"
                    },
                    "direction": {
                        "type": "string",
                        "description": "Navigation direction: up, down, left, right",
                        "enum": ["up", "down", "left", "right"],
                        "default": "down"
                    },
                    "max_steps": {
                        "type": "integer",
                        "description": "Maximum navigation steps (default: 20)",
                        "default": 20
                    },
                    "text_region": {
                        "type": "object",
                        "description": "Region to check for text (if using target_text)",
                        "properties": {
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "width": {"type": "integer"},
                            "height": {"type": "integer"}
                        }
                    }
                }
            }
        ),
    ]
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Execute an STB Tester tool."""
    global connected_device

    try:
        # === Portal/Remote Device Tool Handlers ===

        if name == "stb_list_devices":
            if not PORTAL_AVAILABLE:
                result = {
                    "error": "Portal API not configured",
                    "hint": "Set STBT_PORTAL_URL and STBT_PORTAL_TOKEN environment variables"
                }
            else:
                response = portal_client.list_nodes()
                if "error" in response:
                    result = response
                else:
                    nodes = response.get("nodes", response) if isinstance(response, dict) else response
                    result = {
                        "devices": nodes,
                        "count": len(nodes) if isinstance(nodes, list) else "unknown",
                        "connected_device": connected_device
                    }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stb_connect_device":
            device_id = arguments["device_id"]
            if not PORTAL_AVAILABLE:
                # Mock mode - just track the device ID
                connected_device = device_id
                result = {
                    "status": "connected",
                    "device_id": device_id,
                    "mode": "mock",
                    "message": "Connected in mock mode (Portal API not configured)"
                }
            else:
                # Verify device exists
                response = portal_client.get_node(device_id)
                if "error" in response:
                    result = {"status": "error", "error": response["error"]}
                else:
                    connected_device = device_id
                    result = {
                        "status": "connected",
                        "device_id": device_id,
                        "device_info": response
                    }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stb_device_info":
            device_id = arguments.get("device_id", connected_device)
            if not device_id:
                result = {"error": "No device connected. Use stb_connect_device first or specify device_id."}
            elif not PORTAL_AVAILABLE:
                result = {
                    "device_id": device_id,
                    "status": "mock",
                    "message": "Device info not available in mock mode"
                }
            else:
                response = portal_client.get_node(device_id)
                result = response
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stb_device_screenshot":
            device_id = arguments.get("device_id", connected_device)
            save_path = arguments.get("save_path")

            if not device_id:
                result = {"error": "No device connected. Use stb_connect_device first or specify device_id."}
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            if not PORTAL_AVAILABLE:
                result = {
                    "status": "mock",
                    "device_id": device_id,
                    "message": "Screenshot captured (mock mode - no actual image)"
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            try:
                image_data, content_type = portal_client.get_screenshot(device_id)

                if save_path:
                    with open(save_path, "wb") as f:
                        f.write(image_data)
                    result = {"status": "saved", "path": save_path, "device_id": device_id}
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                else:
                    b64_image = base64.b64encode(image_data).decode("utf-8")
                    return [
                        TextContent(type="text", text=json.dumps({"status": "captured", "device_id": device_id})),
                        ImageContent(type="image", data=b64_image, mimeType=content_type)
                    ]
            except Exception as e:
                result = {"error": str(e), "device_id": device_id}
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stb_device_press":
            key = arguments["key"]
            device_id = arguments.get("device_id", connected_device)

            if not device_id:
                result = {"error": "No device connected. Use stb_connect_device first or specify device_id."}
            elif not PORTAL_AVAILABLE:
                result = {
                    "status": "success",
                    "key": key,
                    "device_id": device_id,
                    "mode": "mock"
                }
            else:
                response = portal_client.press_key(device_id, key)
                if "error" in response:
                    result = response
                else:
                    result = {
                        "status": "success",
                        "key": key,
                        "device_id": device_id
                    }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stb_run_test":
            test_pack = arguments["test_pack"]
            test_case = arguments["test_case"]
            device_id = arguments.get("device_id", connected_device)

            if not device_id:
                result = {"error": "No device connected. Use stb_connect_device first or specify device_id."}
            elif not PORTAL_AVAILABLE:
                result = {
                    "status": "submitted",
                    "job_id": "mock-job-12345",
                    "test_pack": test_pack,
                    "test_case": test_case,
                    "device_id": device_id,
                    "mode": "mock"
                }
            else:
                response = portal_client.run_test(device_id, test_pack, test_case)
                result = response
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stb_job_status":
            job_id = arguments["job_id"]
            if not PORTAL_AVAILABLE:
                result = {
                    "job_id": job_id,
                    "status": "completed",
                    "result": "pass",
                    "mode": "mock"
                }
            else:
                response = portal_client.get_job_status(job_id)
                result = response
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # === Local STB Tester Tool Handlers ===

        elif name == "stb_press":
            key = arguments["key"]
            if STBT_AVAILABLE:
                stbt.press(key)
                result = {"status": "success", "key": key}
            else:
                result = stbt_impl.press(key)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stb_press_and_wait":
            key = arguments["key"]
            stable_secs = arguments.get("stable_secs", 1)
            if STBT_AVAILABLE:
                stbt.press_and_wait(key, stable_secs=stable_secs)
                result = {"status": "success", "key": key, "stable_secs": stable_secs}
            else:
                result = stbt_impl.press_and_wait(key, stable_secs)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stb_press_until_match":
            key = arguments["key"]
            image = arguments["image"]
            max_presses = arguments.get("max_presses", 10)
            interval_secs = arguments.get("interval_secs", 1)
            if STBT_AVAILABLE:
                match_result = stbt.press_until_match(
                    key, image,
                    max_presses=max_presses,
                    interval_secs=interval_secs
                )
                result = {
                    "status": "success",
                    "matched": match_result.match,
                    "position": {
                        "x": match_result.position.x,
                        "y": match_result.position.y
                    } if hasattr(match_result, 'position') else None
                }
            else:
                match_result = stbt_impl.press_until_match(key, image, max_presses, interval_secs)
                result = {"status": "success", "matched": True, "mode": "mock"}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stb_match":
            image = arguments["image"]
            region = region_from_dict(arguments.get("region"))
            if STBT_AVAILABLE:
                if region:
                    match_result = stbt.match(image, region=region)
                else:
                    match_result = stbt.match(image)
                result = {
                    "matched": match_result.match,
                    "confidence": match_result.first_pass_result if hasattr(match_result, 'first_pass_result') else None,
                    "position": {
                        "x": match_result.position.x,
                        "y": match_result.position.y,
                        "width": match_result.position.width,
                        "height": match_result.position.height
                    } if match_result.match and hasattr(match_result, 'position') else None
                }
            else:
                match_result = stbt_impl.match(image, region)
                result = {"matched": True, "confidence": 0.95, "mode": "mock"}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stb_wait_for_match":
            image = arguments["image"]
            timeout_secs = arguments.get("timeout_secs", 10)
            region = region_from_dict(arguments.get("region"))
            try:
                if STBT_AVAILABLE:
                    if region:
                        match_result = stbt.wait_for_match(image, timeout_secs=timeout_secs, region=region)
                    else:
                        match_result = stbt.wait_for_match(image, timeout_secs=timeout_secs)
                    result = {
                        "status": "found",
                        "matched": True,
                        "position": {
                            "x": match_result.position.x,
                            "y": match_result.position.y
                        } if hasattr(match_result, 'position') else None
                    }
                else:
                    result = {"status": "found", "matched": True, "mode": "mock"}
            except Exception as e:
                if "MatchTimeout" in str(type(e)):
                    result = {"status": "timeout", "matched": False, "error": f"Image not found within {timeout_secs}s"}
                else:
                    raise
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stb_wait_for_motion":
            timeout_secs = arguments.get("timeout_secs", 5)
            region = region_from_dict(arguments.get("region"))
            try:
                if STBT_AVAILABLE:
                    if region:
                        stbt.wait_for_motion(timeout_secs=timeout_secs, region=region)
                    else:
                        stbt.wait_for_motion(timeout_secs=timeout_secs)
                    result = {"status": "motion_detected", "motion": True}
                else:
                    result = {"status": "motion_detected", "motion": True, "mode": "mock"}
            except Exception as e:
                if "MotionTimeout" in str(type(e)):
                    result = {"status": "no_motion", "motion": False, "error": f"No motion detected within {timeout_secs}s"}
                else:
                    raise
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stb_ocr":
            region = region_from_dict(arguments.get("region"))
            mode_str = arguments.get("mode")
            if STBT_AVAILABLE:
                ocr_kwargs = {}
                if region:
                    ocr_kwargs["region"] = region
                if mode_str:
                    ocr_kwargs["mode"] = getattr(stbt.OcrMode, mode_str, None)
                text = stbt.ocr(**ocr_kwargs)
                result = {"text": text, "region": str(region) if region else "full_screen"}
            else:
                result = {"text": "Mock OCR Text", "mode": "mock"}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stb_screenshot":
            save_path = arguments.get("save_path")
            if STBT_AVAILABLE:
                frame = stbt.get_frame()
                if frame is not None:
                    import cv2
                    if save_path:
                        cv2.imwrite(save_path, frame)
                        result = {"status": "saved", "path": save_path}
                    else:
                        _, buffer = cv2.imencode('.png', frame)
                        b64_image = base64.b64encode(buffer).decode('utf-8')
                        return [
                            TextContent(type="text", text=json.dumps({"status": "captured"})),
                            ImageContent(type="image", data=b64_image, mimeType="image/png")
                        ]
                else:
                    result = {"status": "error", "error": "No frame available"}
            else:
                result = {"status": "mock", "message": "Screenshot captured (mock mode)"}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stb_get_config":
            section = arguments.get("section", "global")
            key = arguments.get("key")
            if STBT_AVAILABLE:
                try:
                    if key:
                        value = stbt.get_config(section, key)
                        result = {"section": section, "key": key, "value": value}
                    else:
                        result = {"section": section, "message": "Specify a key to retrieve"}
                except Exception as e:
                    result = {"error": str(e)}
            else:
                result = {"section": section, "key": key, "value": "mock_value", "mode": "mock"}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stb_navigate_menu":
            target_image = arguments.get("target_image")
            target_text = arguments.get("target_text")
            direction = arguments.get("direction", "down")
            max_steps = arguments.get("max_steps", 20)
            text_region = region_from_dict(arguments.get("text_region"))

            direction_key = {
                "up": "KEY_UP",
                "down": "KEY_DOWN",
                "left": "KEY_LEFT",
                "right": "KEY_RIGHT"
            }.get(direction, "KEY_DOWN")

            if STBT_AVAILABLE:
                if target_image:
                    # Use press_until_match for image-based navigation
                    try:
                        match_result = stbt.press_until_match(direction_key, target_image, max_presses=max_steps)
                        result = {"status": "found", "method": "image", "matched": True}
                    except Exception:
                        result = {"status": "not_found", "method": "image", "matched": False}
                elif target_text:
                    # Use OCR-based navigation
                    found = False
                    for step in range(max_steps):
                        text = stbt.ocr(region=text_region) if text_region else stbt.ocr()
                        if target_text.lower() in text.lower():
                            found = True
                            break
                        stbt.press(direction_key)
                        await asyncio.sleep(0.5)
                    result = {"status": "found" if found else "not_found", "method": "ocr", "matched": found, "steps": step + 1}
                else:
                    result = {"status": "error", "error": "Must specify target_image or target_text"}
            else:
                result = {"status": "found", "matched": True, "mode": "mock"}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    except Exception as e:
        error_result = {"error": str(e), "type": type(e).__name__}
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


async def main():
    """Run the STB Tester MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
