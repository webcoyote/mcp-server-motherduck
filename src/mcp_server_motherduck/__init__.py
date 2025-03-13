from . import server
import asyncio
import argparse
import logging

logger = logging.getLogger("mcp_server_motherduck")
logging.basicConfig(level=logging.INFO, format="[%(name)s] %(levelname)s - %(message)s")


def main():
    """Main entry point for the package."""

    parser = argparse.ArgumentParser(description="MotherDuck MCP Server")
    parser.add_argument(
        "--db-path",
        help="Path to local DuckDB database file",
    )
    parser.add_argument(
        "--motherduck-token",
        default=None,
        help="Access token to use for MotherDuck database connections",
    )
    parser.add_argument(
        "--home-dir",
        default=None,
        help="Home directory for DuckDB",
    )
    # This is experimental and will change in the future
    parser.add_argument(
        "--result-format",
        help="Format of the output",
        default="markdown",
        choices=["markdown", "duckbox", "text"],
    )

    args = parser.parse_args()
    logger.info("🦆 MotherDuck MCP Server v" + server.SERVER_VERSION)
    logger.info("Ready to execute SQL queries via DuckDB/MotherDuck")
    logger.info("Waiting for client connection...\n")

    asyncio.run(
        server.main(
            db_path=args.db_path,
            motherduck_token=args.motherduck_token,
            result_format=args.result_format,
            home_dir=args.home_dir,
        )
    )


# Optionally expose other important items at package level
__all__ = ["main", "server"]
