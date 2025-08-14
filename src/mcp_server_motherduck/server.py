import logging
from pydantic import AnyUrl
from typing import Literal
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from .configs import SERVER_VERSION
from .database import DatabaseClient
from .prompt import PROMPT_TEMPLATE


logger = logging.getLogger("mcp_server_motherduck")


def build_application(
    db_path: str | None = None,
    motherduck_token: str | None = None,
    home_dir: str | None = None,
    saas_mode: bool = False,
    read_only: bool = False,
):
    logger.info("Starting MotherDuck MCP Server with dynamic database support")
    server = Server("mcp-server-motherduck")
    current_db_path = db_path if db_path else "md:"
    db_client = DatabaseClient(
        motherduck_token=motherduck_token,
        home_dir=home_dir,
        saas_mode=saas_mode,
        read_only=read_only,
    )
    

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
        nonlocal current_db_path
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
                        "db_path": {
                            "type": "string",
                            "description": f"Path to the database (e.g., ':memory:', 'path/to/database.db', 'md:my_database'). Defaults to '{current_db_path}' if not specified.",
                        },
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="list_databases",
                description="List available databases including MotherDuck databases and local DuckDB files",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="set_database",
                description="Set the database path for future queries",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "db_path": {
                            "type": "string",
                            "description": "The database path to set as (e.g., 'md:', ':memory:', 'path/to/database.db')",
                        },
                    },
                    "required": ["db_path"],
                },
            ),
            types.Tool(
                name="get_database",
                description="Get the current database path",
                inputSchema={
                    "type": "object",
                    "properties": {},
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
        nonlocal current_db_path
        logger.info(f"Calling tool: {name}::{arguments}")
        try:
            if name == "query":
                if arguments is None:
                    return [
                        types.TextContent(type="text", text="Error: No query provided")
                    ]
                query = arguments["query"]
                db_path = arguments.get("db_path", current_db_path)
                tool_response = db_client.query(query, db_path)
                return [types.TextContent(type="text", text=str(tool_response))]
            
            elif name == "list_databases":
                databases = db_client.list_available_databases()
                return [types.TextContent(type="text", text=databases)]
            
            elif name == "set_database":
                if arguments is None or "db_path" not in arguments:
                    return [
                        types.TextContent(type="text", text="Error: No database path provided")
                    ]
                new_path = arguments["db_path"]
                # Validate the path is accessible
                try:
                    db_client.validate_database_path(new_path)
                    current_db_path = new_path
                    return [types.TextContent(
                        type="text", 
                        text=f"Database path changed to '{current_db_path}'"
                    )]
                except Exception as e:
                    return [types.TextContent(
                        type="text", 
                        text=f"Error setting database path: {str(e)}"
                    )]
            
            elif name == "get_database":
                return [types.TextContent(
                    type="text", 
                    text=f"Current database path: '{current_db_path}'"
                )]

            return [types.TextContent(type="text", text=f"Unsupported tool: {name}")]

        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            raise ValueError(f"Error executing tool {name}: {str(e)}")

    initialization_options = InitializationOptions(
        server_name="motherduck",
        server_version=SERVER_VERSION,
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )

    return server, initialization_options
