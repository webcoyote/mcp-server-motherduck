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
    args = parser.parse_args()

    # Print welcome message
    print("\n🦆 MotherDuck MCP Server v" + server.SERVER_VERSION, flush=True)
    print("Ready to execute SQL queries via DuckDB/MotherDuck", flush=True)
    print(
        "Server running in "
        + ("MotherDuck mode" if args.db_path and args.db_path.startswith("md:") else "DuckDB mode"),
        flush=True,
    )
    print("Waiting for client connection...\n", flush=True)

    # Run the server
    asyncio.run(server.main(db_path=args.db_path))


# Optionally expose other important items at package level
__all__ = ["main", "server"]
