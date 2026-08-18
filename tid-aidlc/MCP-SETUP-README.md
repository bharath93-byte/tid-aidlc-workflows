# MCP setup

To use Jira (and other MCP tools) in Cursor, create the config file.

1. Create **`.cursor/mcp.json`** in the repo root.

2. Add:

```json
{
  "mcpServers": {
    "jira": {
      "command": "npx",
      "args": ["-y", "@atlassian-dc-mcp/jira"],
      "env": {
        "JIRA_HOST": "jira.trimble.tools",
        "JIRA_API_TOKEN": "<your-jira-pat-token>"
      }
    }
  }
}
```

3. Replace `<your-jira-pat-token>` with your Jira PAT token.

4. Restart Cursor.

5. Make sure the mcp is enabled in cursor settings
Requires Node.js (for `npx`).
