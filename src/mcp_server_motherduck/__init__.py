from . import server
import asyncio
import argparse
import logging

logger = logging.getLogger("mcp_server_motherduck")


def main():
    """Main entry point for the package."""
    logging.basicConfig(
        level=logging.INFO, format="%(Y-%m-%d %H:%M)s - %(levelname)s - %(message)s"
    )

    parser = argparse.ArgumentParser(description="MotherDuck MCP Server")
    parser.add_argument(
        "--db-path",
        help="Path to local DuckDB database file",
    )
    # This is experimental and will change in the future
    parser.add_argument(
        "--result-format",
        help="Format of the output",
        default="markdown",
        choices=["markdown", "duckbox", "text"],
    )

    args = parser.parse_args()

    logger.info("\n🦆 MotherDuck MCP Server v" + server.SERVER_VERSION)
    logger.info("Ready to execute SQL queries via DuckDB/MotherDuck")
    logger.info(
        "Server running in "
        + ("MotherDuck mode" if args.db_path and args.db_path.startswith("md:") else "DuckDB mode")
    )
    logger.info("Waiting for client connection...\n")

    asyncio.run(server.main(db_path=args.db_path, result_format=args.result_format))


# Optionally expose other important items at package level
__all__ = ["main", "server"]
