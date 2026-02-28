#!/usr/bin/env python3
"""List all available MCP tools from NotebookLM server"""
import subprocess
import json
import time

def json_rpc(method, params=None, id=None):
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    if id is not None:
        msg["id"] = id
    return json.dumps(msg)

cmd = ["uv", "tool", "run", "notebooklm-mcp", "server"]

print("🚀 Starting NotebookLM MCP Server...")
proc = subprocess.Popen(
    cmd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

time.sleep(2)

# Initialize
init_req = json_rpc("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "tools-lister", "version": "1.0"}
}, id=1)

proc.stdin.write(init_req + "\n")
proc.stdin.flush()

# Wait for init response
while True:
    line = proc.stdout.readline()
    if not line:
        break
    try:
        resp = json.loads(line)
        if resp.get("id") == 1:
            print("✅ Connected to MCP server\n")
            break
    except json.JSONDecodeError:
        pass

# Initialized notification
notif = json_rpc("notifications/initialized")
proc.stdin.write(notif + "\n")
proc.stdin.flush()

# List all tools
tools_req = json_rpc("tools/list", id=2)
proc.stdin.write(tools_req + "\n")
proc.stdin.flush()

print("=" * 80)
print("AVAILABLE MCP TOOLS")
print("=" * 80)

while True:
    line = proc.stdout.readline()
    if not line:
        break
    try:
        resp = json.loads(line)
        if resp.get("id") == 2:
            tools = resp.get("result", {}).get("tools", [])
            print(f"\n📊 Total Tools: {len(tools)}\n")

            for i, tool in enumerate(tools, 1):
                print(f"\n{'─' * 80}")
                print(f"🔧 TOOL #{i}: {tool['name']}")
                print(f"{'─' * 80}")
                print(f"📝 Description: {tool.get('description', 'No description')}")

                if 'inputSchema' in tool:
                    schema = tool['inputSchema']
                    print(f"\n📋 Input Schema:")
                    print(json.dumps(schema, indent=2))

            print(f"\n{'=' * 80}\n")
            break
    except json.JSONDecodeError:
        pass

proc.terminate()
