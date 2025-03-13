from . import server
import asyncio
import argparse


def main():
    """Main entry point for the package."""
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

    print("\n🦆 MotherDuck MCP Server v" + server.SERVER_VERSION, flush=True)
    print("Ready to execute SQL queries via DuckDB/MotherDuck", flush=True)
    print(
        "Server running in "
        + ("MotherDuck mode" if args.db_path and args.db_path.startswith("md:") else "DuckDB mode"),
        flush=True,
    )
    print("Waiting for client connection...\n", flush=True)

    asyncio.run(server.main(db_path=args.db_path, result_format=args.result_format))


# Optionally expose other important items at package level
__all__ = ["main", "server"]
