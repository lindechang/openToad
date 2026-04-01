#!/usr/bin/env python3
import asyncio
import json
import sys
import uuid
import websockets


async def test_client(instance_id: str = None, host: str = "localhost", port: int = 18989):
    instance_id = instance_id or str(uuid.uuid4())
    uri = f"ws://{host}:{port}/ws"
    
    print(f"Connecting to {uri}...")
    print(f"Using instance_id: {instance_id}")
    print()

    try:
        async with websockets.connect(uri, open_timeout=10, close_timeout=5) as ws:
            auth_msg = {
                "type": "auth",
                "payload": {"instance_id": instance_id}
            }
            await ws.send(json.dumps(auth_msg))
            
            response = await ws.recv()
            data = json.loads(response)
            print(f"Auth response: {json.dumps(data, indent=2)}")
            print()

            if not data.get("payload", {}).get("success"):
                print("Authentication failed!")
                return

            test_message = "Hello, this is a test message from the mobile app!"
            print(f"Sending message: {test_message}")
            msg = {
                "type": "message",
                "payload": {"content": test_message, "stream": True}
            }
            await ws.send(json.dumps(msg))
            print()

            print("Receiving response:")
            while True:
                response = await ws.recv()
                data = json.loads(response)
                if data.get("type") == "response":
                    content = data.get("payload", {}).get("content", "")
                    done = data.get("payload", {}).get("done", False)
                    if content:
                        print(content, end="", flush=True)
                    if done:
                        print()
                        break
                elif data.get("type") == "error":
                    print(f"Error: {data.get('payload')}")
                    break
                elif data.get("type") == "pong":
                    print("Pong received")

    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="WebSocket Gateway Test Client")
    parser.add_argument("--instance-id", help="Instance ID to use")
    parser.add_argument("--host", default="localhost", help="Gateway host")
    parser.add_argument("--port", type=int, default=18989, help="Gateway port")
    args = parser.parse_args()

    asyncio.run(test_client(args.instance_id, args.host, args.port))
