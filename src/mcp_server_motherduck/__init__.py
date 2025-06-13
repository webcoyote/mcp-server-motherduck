import anyio
import logging
import click
from .server import build_application
from .configs import SERVER_VERSION

logger = logging.getLogger("mcp_server_motherduck")
logging.basicConfig(level=logging.INFO, format="[%(name)s] %(levelname)s - %(message)s")


@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="(Default: `stdio`) Transport type",
)
@click.option(
    "--db-path",
    default="md:",
    help="(Default: `md:`) Path to local DuckDB database file or MotherDuck database",
)
@click.option(
    "--motherduck-token",
    default=None,
    help="(Default: env var `motherduck_token`) Access token to use for MotherDuck database connections",
)
@click.option(
    "--home-dir",
    default=None,
    help="(Default: env var `HOME`) Home directory for DuckDB",
)
@click.option(
    "--saas-mode",
    is_flag=True,
    help="Flag for connecting to MotherDuck in SaaS mode",
)
@click.option(
    "--result-format",
    default="markdown",
    type=click.Choice(["markdown", "duckbox", "text"]),
    help="(Default: `markdown`) Format of the query result",
)
@click.option(
    "--read-only",
    is_flag=True,
    help="Flag for connecting to DuckDB in read-only mode. Only supported for local DuckDB databases. Also makes use of short lived connections so multiple MCP clients or other systems can remain active (though each operation must be done sequentially).",
)
def main(
    port,
    transport,
    db_path,
    motherduck_token,
    home_dir,
    saas_mode,
    result_format,
    read_only,
):
    """Main entry point for the package."""

    logger.info("🦆 MotherDuck MCP Server v" + SERVER_VERSION)
    logger.info("Ready to execute SQL queries via DuckDB/MotherDuck")
    logger.info("Waiting for client connection...")

    app, init_opts = build_application(
        db_path=db_path,
        motherduck_token=motherduck_token,
        result_format=result_format,
        home_dir=home_dir,
        saas_mode=saas_mode,
        read_only=read_only,
    )

    if transport == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.responses import Response
        from starlette.routing import Mount, Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as (read_stream, write_stream):
                await app.run(read_stream, write_stream, init_opts)
            return Response()

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse, methods=["GET"]),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        import uvicorn

        uvicorn.run(starlette_app, host="127.0.0.1", port=port)
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as (read_stream, write_stream):
                await app.run(read_stream, write_stream, init_opts)

        anyio.run(arun)

    # This will only be reached when the server is shutting down
    logger.info("\n🦆 MotherDuck MCP Server shutting down...")


# Optionally expose other important items at package level
__all__ = ["main"]

if __name__ == "__main__":
    main()
