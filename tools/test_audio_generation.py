#!/usr/bin/env python3
"""
Script para testar a geração de Audio Overview do notebook Docker via MCP NotebookLM
"""
import subprocess
import json
import sys
import time

def json_rpc(method, params=None, id=None):
    """Create a JSON-RPC message"""
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    if id is not None:
        msg["id"] = id
    return json.dumps(msg)

def send_and_receive(proc, message, request_id):
    """Send a message and wait for response"""
    print(f"\n📤 Sending: {message[:100]}...")
    proc.stdin.write(message + "\n")
    proc.stdin.flush()

    while True:
        line = proc.stdout.readline()
        if not line:
            break
        try:
            resp = json.loads(line)
            if resp.get("id") == request_id:
                return resp
        except json.JSONDecodeError:
            continue
    return None

# Notebook Docker ID
DOCKER_NOTEBOOK_ID = "85d38ec1-7659-4307-aedf-3bc773a4d4ba"

print("🚀 Starting NotebookLM MCP Server...")
cmd = ["uv", "tool", "run", "notebooklm-mcp", "server"]

proc = subprocess.Popen(
    cmd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

# Give it time to start
time.sleep(2)

# 1. Initialize
print("\n🔧 Initializing MCP connection...")
init_req = json_rpc("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "audio-test-client", "version": "1.0"}
}, id=1)

resp = send_and_receive(proc, init_req, 1)
if resp and resp.get("result"):
    print("✅ Initialized successfully!")
else:
    print("❌ Failed to initialize")
    proc.terminate()
    sys.exit(1)

# 2. Initialized notification
notif = json_rpc("notifications/initialized")
proc.stdin.write(notif + "\n")
proc.stdin.flush()

# 3. List all tools to see if studio_create is available
print("\n📋 Listing available tools...")
tools_req = json_rpc("tools/list", id=2)
resp = send_and_receive(proc, tools_req, 2)

if resp and "result" in resp:
    tools = resp["result"].get("tools", [])
    print(f"\n✅ Found {len(tools)} tools:")

    studio_create_found = False
    for tool in tools:
        name = tool.get("name", "")
        desc = tool.get("description", "")

        if "studio" in name.lower() or "audio" in name.lower():
            print(f"\n🎙️  {name}")
            print(f"   📝 {desc}")
            if "inputSchema" in tool:
                print(f"   📄 Args: {json.dumps(tool['inputSchema'], indent=6)}")

            if name == "studio_create":
                studio_create_found = True

    if not studio_create_found:
        print("\n⚠️  Tool 'studio_create' not found!")
        print("   Available tools that might help:")
        for tool in tools:
            if any(keyword in tool.get("name", "").lower()
                   for keyword in ["create", "generate", "audio"]):
                print(f"   - {tool['name']}: {tool.get('description', '')[:80]}...")
else:
    print("❌ Failed to list tools")

# 4. If studio_create is available, try to create an audio overview
# Note: This may require authentication first
if studio_create_found:
    print(f"\n🎵 Attempting to create Audio Overview for Docker notebook...")
    print(f"   Notebook ID: {DOCKER_NOTEBOOK_ID}")

    # This might fail if not authenticated - but let's try
    audio_req = json_rpc("tools/call", {
        "name": "studio_create",
        "arguments": {
            "notebook_id": DOCKER_NOTEBOOK_ID,
            "artifact_type": "audio_overview",  # or "podcast"
            "format": "deep_dive"  # or other available formats
        }
    }, id=3)

    resp = send_and_receive(proc, audio_req, 3)

    if resp:
        if "error" in resp:
            print(f"\n❌ Error: {resp['error']}")
            print("   This likely means authentication is required.")
        elif "result" in resp:
            print(f"\n✅ Success! Response:")
            print(json.dumps(resp["result"], indent=2))
    else:
        print("\n⚠️  No response received")

proc.terminate()
print("\n✅ Test complete.")
