#!/usr/bin/env python3
"""Simple STB Tester CLI for testing Portal API connection."""

import json
import urllib.request
import urllib.error
import sys

# Configuration
PORTAL_URL = "https://ziggo.stb-tester.com"
PORTAL_TOKEN = "cBqdzRDwYbX1LI6cmskfsycAXNAIZPSs"
DEVICE_ID = "stb-tester-48b02d5b0ab7"


class PortalClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
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

    def list_nodes(self) -> dict:
        return self._request("GET", "/nodes")

    def get_node(self, node_id: str) -> dict:
        return self._request("GET", f"/nodes/{node_id}")

    def press_key(self, node_id: str, key: str) -> dict:
        return self._request("POST", f"/nodes/{node_id}/press", {"key": key})


def main():
    print("=" * 50)
    print("STB Tester CLI - Connecting to Portal")
    print("=" * 50)
    print(f"Portal URL: {PORTAL_URL}")
    print(f"Device ID: {DEVICE_ID}")
    print()

    client = PortalClient(PORTAL_URL, PORTAL_TOKEN)

    # Test 1: List devices
    print("[1] Listing available devices...")
    result = client.list_nodes()
    print(json.dumps(result, indent=2))
    print()

    # Test 2: Get device info
    print(f"[2] Getting info for device: {DEVICE_ID}...")
    result = client.get_node(DEVICE_ID)
    print(json.dumps(result, indent=2))
    print()

    print("=" * 50)
    print("Connection test complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
