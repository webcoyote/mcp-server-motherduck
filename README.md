# mcp-server-motherduck

An MCP server implementation that integrates MotherDuck and local DuckDB, providing SQL analytics capabilities to Claude.

## Installation

To install and run the server:

1. Install the package using `uvx`:

   ```bash
   pip install uvx
   uvx install mcp-server-motherduck
   ```

2. Start the server manually (for testing):

   ```bash
   uvx mcp-server-motherduck
   ```

The server is designed to be run by tools like Claude Desktop or Cursor, but you can start it manually for testing purposes.

## Features

- **Hybrid execution**: query data from both local DuckDB and cloud-based MotherDuck seamlessly
- **Cloud storage integration**: access data stored in Amazon S3 or other cloud storage
- **Data sharing**: share database snapshots with colleagues
- **SQL analytics**: leverage the full power of DuckDB's SQL dialect
- **Serverless architecture**: no need to configure instances or clusters

## Components

### Prompts

The server provides one prompt:

- `duckdb-motherduck-prompt`: A prompt to initialize a connection to DuckDB or MotherDuck and start working with it

### Tools

The server offers one tool:

- `query`: Execute a SQL query on the MotherDuck/DuckDB database
  - **Inputs**:
    - `query` (string, required): The SQL query to execute

All interactions with both DuckDB and MotherDuck are done through writing SQL queries, providing a unified interface for data analysis.

## Getting Started

### Prerequisites

- A MotherDuck account (sign up at [motherduck.com](https://motherduck.com))
- A MotherDuck access token
- Claude Desktop installed

### Setting up your MotherDuck token

1. Sign up for a [MotherDuck account](https://app.motherduck.com/?auth_flow=signup)
2. Generate an access token via the [MotherDuck UI](https://app.motherduck.com/settings/tokens?auth_flow=signup)
3. Store the token securely for use in the configuration

### Usage with Claude Desktop

1. Install Claude Desktop from [claude.ai/download](https://claude.ai/download) if you haven't already

2. Open the Claude Desktop configuration file:

- To quickly access it or create it the first time, open the Claude Desktop app, select Settings, and click on the "Developer" tab, finally click on the "Edit Config" button.
- Add the following configuration to your `claude_desktop_config.json`:

```json
"mcpServers": {
  "mcp-server-motherduck": {
    "command": "uvx",
    "args": [
      "mcp-server-motherduck"
    ],
    "env": {
      "motherduck_token": "YOUR_MOTHERDUCK_TOKEN_HERE",
      "HOME": "YOUR_HOME_FOLDER_PATH"
    }
  }
}
```

**Important Notes**:

- Replace `YOUR_MOTHERDUCK_TOKEN_HERE` with your actual MotherDuck token
- Replace `YOUR_HOME_FOLDER_PATH` with the path to your home directory (needed by DuckDB for file operations). For example, on macOS, it would be `~/Users/your_username`
- The `HOME` environment variable is required for DuckDB to function properly

### Usage with Cursor

1. Install Cursor from [cursor.sh](https://cursor.sh) if you haven't already

2. Configure the MCP server in Cursor:
   - Go to `Cursor Settings` > `Features` > `MCP`
   - Click on the `+ Add New MCP Server` button
   - Fill out the form:
     - **Name**: `mcp-server-motherduck` (or any name you prefer)
     - **Type**: Select `stdio`
     - **Command**: `uvx mcp-server-motherduck`
   - Click `Add Server`

3. Alternatively, you can configure project-specific MCP settings by creating a `.cursor/mcp.json` file in your project root:

   ```json
   {
     "mcpServers": {
       "mcp-server-motherduck": {
         "command": "uvx",
         "args": ["mcp-server-motherduck"],
         "env": {
           "motherduck_token": "YOUR_MOTHERDUCK_TOKEN_HERE",
           "HOME": "YOUR_HOME_FOLDER_PATH"
         }
       }
     }
   }
   ```

4. After adding the server, it should appear in the list of MCP servers. You may need to press the refresh button in the top right corner of the MCP server to populate the tool list.

5. Use the MCP tools in Cursor's Composer Agent by asking it to run SQL queries against MotherDuck or DuckDB.

**Important Notes**:

- Replace `YOUR_MOTHERDUCK_TOKEN_HERE` with your actual MotherDuck token
- Replace `YOUR_HOME_FOLDER_PATH` with the path to your home directory (needed by DuckDB for file operations). For example, on macOS, it would be `/Users/your_username`
- The `HOME` environment variable is required for DuckDB to function properly
- MCP tools are only available to the Agent in Composer

## Example Queries

Once configured, you can ask Claude to run queries like:

- "Create a new database and table in MotherDuck"
- "Query data from my local CSV file"
- "Join data from my local DuckDB database with a table in MotherDuck"
- "Analyze data stored in Amazon S3"

## Testing

When testing the server manually, you can specify which database to connect to using the `--db-path` parameter:

1. **Default MotherDuck database**:

   ```bash
   uvx mcp-server-motherduck --db-path md:
   ```

2. **Specific MotherDuck database**:

   ```bash
   uvx mcp-server-motherduck --db-path md:your_database_name
   ```

3. **Local DuckDB database**:

   ```bash
   uvx mcp-server-motherduck --db-path /path/to/your/local.db
   ```

4. **In-memory database** (default if no path and no token):

   ```bash
   uvx mcp-server-motherduck
   ```


If you don't specify a database path but have set the `motherduck_token` environment variable, the server will automatically connect to the default MotherDuck database (`md:`).

## Troubleshooting

- If you encounter connection issues, verify your MotherDuck token is correct
- For local file access problems, ensure the `HOME` environment variable is set correctly
- Check that the `uvx` command is available in your PATH

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
