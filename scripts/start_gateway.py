#!/usr/bin/env python3
import argparse
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.gateway import GatewayServer, GatewayConfig, AIHandler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="OpenToad WebSocket Gateway")
    parser.add_argument("--host", default="0.0.0.0", help="Gateway host")
    parser.add_argument("--port", type=int, default=18989, help="Gateway port")
    parser.add_argument("--provider", default=os.getenv("OPENAI_PROVIDER", "openai"), help="LLM provider")
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""), help="API key")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), help="Model name")
    parser.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", ""), help="Base URL for provider")
    parser.add_argument("--no-stream", action="store_true", help="Disable streaming")
    args = parser.parse_args()

    ai_handler = AIHandler(
        provider_type=args.provider,
        api_key=args.api_key,
        model=args.model,
        base_url=args.base_url or None,
        stream=not args.no_stream
    )

    async def handle_message(instance_id: str, content: str):
        async for chunk in ai_handler.handle_message(instance_id, content):
            yield chunk

    config = GatewayConfig(host=args.host, port=args.port)
    gateway = GatewayServer(config=config, on_message=handle_message)

    logger.info(f"Starting OpenToad Gateway on {args.host}:{args.port}")
    logger.info(f"Using provider: {args.provider}, model: {args.model}")
    logger.info("WebSocket endpoint: ws://{args.host}:{args.port}/ws")

    gateway.start()


if __name__ == "__main__":
    main()
