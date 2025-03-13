import os
import logging
import duckdb
from pydantic import AnyUrl
from typing import Literal
import io
from contextlib import redirect_stdout
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from .prompt import PROMPT_TEMPLATE


SERVER_VERSION = "0.3.4"

logger = logging.getLogger("mcp_server_motherduck")


class DatabaseClient:
    def __init__(
        self,
        db_path: str | None = None,
        result_format: Literal["markdown", "duckbox", "text"] = "markdown",
    ):
        self.db_path, self.db_type = self._resolve_db_path_type(db_path)
        logger.info(f"Database client initialized in `{self.db_type}` mode")

        self.conn = self._initialize_connection()
        self.result_format = result_format

    def _initialize_connection(self) -> duckdb.DuckDBPyConnection:
        """Initialize connection to the MotherDuck or DuckDB database"""

        logger.info(f"🔌 Connecting to {self.db_type} database: {self.db_path}")

        conn = duckdb.connect(
            self.db_path,
            config={"custom_user_agent": f"mcp-server-motherduck/{SERVER_VERSION}"},
        )

        logger.info(f"✅ Successfully connected to {self.db_type} database")

        return conn

    def _resolve_db_path_type(
        self, db_path: str | None = None
    ) -> tuple[str, Literal["duckdb", "motherduck"]]:
        """Resolve and validate the database path"""
        # Use MotherDuck if token is available and no path specified
        if db_path is None and os.getenv("motherduck_token"):
            logger.info("Using MotherDuck token to connect to database `md:`")
            return "md:", "motherduck"

        # Handle MotherDuck paths
        if db_path and (db_path == "md:" or db_path.startswith("md:")):
            if not os.getenv("motherduck_token"):
                raise ValueError(
                    "Please set the `motherduck_token` environment variable when using `md:` as db_path."
                )
            return db_path, "motherduck"

        # Handle local database paths
        if db_path:
            if not os.path.exists(db_path):
                raise FileNotFoundError(
                    f"The database path `{db_path}` does not exist."
                )
            return db_path, "duckdb"

        # Default to in-memory database
        return ":memory:", "duckdb"

    def query(self, query: str) -> str:
        try:
            if self.result_format == "markdown":
                # Markdown version of the output
                logger.info(
                    f"🔍 Executing query: {query[:60]}{'...' if len(query) > 60 else ''}"
                )
                result = self.conn.execute(query).fetchdf().to_markdown()
                logger.info("✅ Query executed successfully")
                return result
            elif self.result_format == "duckbox":
                # Duckbox version of the output
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    self.conn.sql(query).show(max_rows=100, max_col_width=20)
                return buffer.getvalue()
            else:
                # Text version of the output
                return str(self.conn.execute(query).fetchall())

        except Exception as e:
            raise ValueError(f"❌ Error executing query: {e}")

    def mcp_config(self) -> dict[str, str]:
        """Used for debugging purposes to show the current MCP config"""
        return {
            "current_working_directory": os.getcwd(),
            "database_type": self.db_type,
            "database_path": self.db_path,
        }


async def main(
    db_path: str, result_format: Literal["markdown", "duckbox", "text"] = "markdown"
):
    logger.info(f"Starting MotherDuck MCP Server with DB path: {db_path}")
    server = Server("mcp-server-motherduck")
    db_client = DatabaseClient(db_path=db_path, result_format=result_format)

    logger.info("Registering handlers")

    @server.list_resources()
    async def handle_list_resources() -> list[types.Resource]:
        """
        List available note resources.
        Each note is exposed as a resource with a custom note:// URI scheme.
        """
        logger.info("No resources available to list")
        return []

    @server.read_resource()
    async def handle_read_resource(uri: AnyUrl) -> str:
        """
        Read a specific note's content by its URI.
        The note name is extracted from the URI host component.
        """
        logger.info(f"Reading resource: {uri}")
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    @server.list_prompts()
    async def handle_list_prompts() -> list[types.Prompt]:
        """
        List available prompts.
        Each prompt can have optional arguments to customize its behavior.
        """
        logger.info("Listing prompts")
        # TODO: Check where and how this is used, and how to optimize this.
        # Check postgres and sqlite servers.
        return [
            types.Prompt(
                name="duckdb-motherduck-initial-prompt",
                description="A prompt to initialize a connection to duckdb or motherduck and start working with it",
            )
        ]

    @server.get_prompt()
    async def handle_get_prompt(
        name: str, arguments: dict[str, str] | None
    ) -> types.GetPromptResult:
        """
        Generate a prompt by combining arguments with server state.
        The prompt includes all current notes and can be customized via arguments.
        """
        logger.info(f"Getting prompt: {name}::{arguments}")
        # TODO: Check where and how this is used, and how to optimize this.
        # Check postgres and sqlite servers.
        if name != "duckdb-motherduck-initial-prompt":
            raise ValueError(f"Unknown prompt: {name}")

        return types.GetPromptResult(
            description="Initial prompt for interacting with DuckDB/MotherDuck",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=PROMPT_TEMPLATE),
                )
            ],
        )

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """
        List available tools.
        Each tool specifies its arguments using JSON Schema validation.
        """
        logger.info("Listing tools")
        return [
            types.Tool(
                name="query",
                description="Use this to execute a query on the MotherDuck or DuckDB database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SQL query to execute that is a dialect of DuckDB SQL",
                        },
                    },
                    "required": ["query"],
                },
            ),
        ]

    @server.call_tool()
    async def handle_tool_call(
        name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        Handle tool execution requests.
        Tools can modify server state and notify clients of changes.
        """
        logger.info(f"Calling tool: {name}::{arguments}")
        try:
            if name == "query":
                if arguments is None:
                    return [
                        types.TextContent(type="text", text="Error: No query provided")
                    ]
                tool_response = db_client.query(arguments["query"])
                return [types.TextContent(type="text", text=str(tool_response))]

            return [types.TextContent(type="text", text=f"Unsupported tool: {name}")]

        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            raise ValueError(f"Error executing tool {name}: {str(e)}")

    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="motherduck",
                server_version=SERVER_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

        # This will only be reached when the server is shutting down
        logger.info("\n🦆 MotherDuck MCP Server shutting down...")
        logger.info(f"Database connection to {db_client.db_path} closed.")
