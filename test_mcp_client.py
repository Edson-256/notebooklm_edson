import subprocess
import json
import sys
import os
import time

def json_rpc(method, params=None, id=None):
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    if id is not None:
        msg["id"] = id
    return json.dumps(msg)

cmd = ["uv", "tool", "run", "notebooklm-mcp", "server"] 

print(f"Starting server with command: {' '.join(cmd)}")
proc = subprocess.Popen(
    cmd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=sys.stderr, 
    text=True,
    bufsize=1 
)

# 1. Initialize
init_req = json_rpc("initialize", {
    "protocolVersion": "2024-11-05", # Updated protocol version
    "capabilities": {},
    "clientInfo": {"name": "test-client", "version": "1.0"}
}, id=1)

print(f"Sending Initialize...")
proc.stdin.write(init_req + "\n")
proc.stdin.flush()

# Read response
while True:
    line = proc.stdout.readline()
    if not line:
        break
    # print(f"DEBUG: {line.strip()}")
    try:
        resp = json.loads(line)
        if resp.get("id") == 1:
            print("Initialized successfully!")
            break
    except json.JSONDecodeError:
        pass

# 2. Initialized notification
notif = json_rpc("notifications/initialized")
proc.stdin.write(notif + "\n")
proc.stdin.flush()

# 3. List Resources
list_req = json_rpc("resources/list", id=2)
print(f"Sending List Resources...")
proc.stdin.write(list_req + "\n")
proc.stdin.flush()

# Read response for resources
while True:
    line = proc.stdout.readline()
    if not line:
        break
    try:
        resp = json.loads(line)
        if resp.get("id") == 2:
            print("\n Notebooks (Resources) Found:")
            result = resp.get("result", {})
            resources = result.get("resources", [])
            if not resources:
                print("No resources found.")
            for res in resources:
                print(f"- {res['name']} (URI: {res['uri']})")
            break
    except json.JSONDecodeError:
        pass

# 4. List Tools and Print Arguments
tools_req = json_rpc("tools/list", id=3)
print(f"Sending List Tools...")
proc.stdin.write(tools_req + "\n")
proc.stdin.flush()

# Read response for tools
while True:
    line = proc.stdout.readline()
    if not line:
        break
    try:
        resp = json.loads(line)
        if resp.get("id") == 3:
            print("\n Tools Found:")
            result = resp.get("result", {})
            tools = result.get("tools", [])
            for tool in tools:
                print(f"\nTool: {tool['name']}")
                print(f"Desc: {tool.get('description', 'No description')}")
                if 'inputSchema' in tool:
                     print(f"Args: {json.dumps(tool['inputSchema'], indent=2)}")
            break
    except json.JSONDecodeError:
        pass

# 5. Call notebook_list directly
call_req = json_rpc("tools/call", {"name": "notebook_list", "arguments": {}}, id=4)
print(f"Calling notebook_list tool directly to see if it works...")
proc.stdin.write(call_req + "\n")
proc.stdin.flush()

# Read response for call
while True:
    line = proc.stdout.readline()
    if not line:
        break
    try:
        resp = json.loads(line)
        if resp.get("id") == 4:
            print("\n Notebook List Result:")
            if "error" in resp:
                print(f"Error: {resp['error']}")
            else:
                result = resp.get("result", {})
                content = result.get("content", [])
                for item in content:
                    if item.get("type") == "text":
                        print(item.get("text"))
            break
    except json.JSONDecodeError:
        pass

# 6. Call get_default_notebook
call_req = json_rpc("tools/call", {"name": "get_default_notebook", "arguments": {}}, id=5)
print(f"Calling get_default_notebook tool...")
proc.stdin.write(call_req + "\n")
proc.stdin.flush()

# Read response for call
while True:
    line = proc.stdout.readline()
    if not line:
        break
    try:
        resp = json.loads(line)
        if resp.get("id") == 5:
            print("\n Default Notebook Result:")
            if "error" in resp:
                print(f"Error: {resp['error']}")
            else:
                result = resp.get("result", {})
                content = result.get("content", [])
                for item in content:
                    if item.get("type") == "text":
                        print(item.get("text"))
            break
    except json.JSONDecodeError:
        pass

proc.terminate()
print("\nTest complete.")
