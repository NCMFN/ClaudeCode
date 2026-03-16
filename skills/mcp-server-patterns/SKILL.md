---
name: mcp-server-patterns
description: Build MCP servers with Node/TypeScript SDK — registerTool/registerResource, Zod validation, stdio vs HTTP. Use Context7 or official MCP docs for latest API.
origin: ECC
---

# MCP Server Patterns

The Model Context Protocol (MCP) lets AI assistants call tools and read resources from your server. Use this skill when building or maintaining MCP servers. For the latest SDK API, use Context7 (query-docs) or the official MCP documentation; the SDK evolves quickly.

## Core Concepts

- **Tools**: Actions the model can invoke (e.g. search, run a command). Register with `registerTool()` (or the current SDK equivalent).
- **Resources**: Read-only data the model can fetch (e.g. file contents, API responses). Register with `registerResource()`.
- **Transport**: stdio for local clients (e.g. Claude Desktop); HTTP/SSE for remote (e.g. Cursor, cloud).

## Node.js / TypeScript SDK

Install and use the official SDK. Prefer **registerTool** and **registerResource**; avoid deprecated `tool()` / `resource()` if your SDK version has moved on.

```bash
npm install @modelcontextprotocol/sdk zod
```

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({
  name: "my-server",
  version: "1.0.0",
});

// Prefer registerTool with a schema (Zod or JSON Schema)
server.registerTool({
  name: "echo",
  description: "Echo a message",
  inputSchema: z.object({
    message: z.string().describe("Message to echo"),
  }),
  handler: async ({ message }) => ({ content: [{ type: "text", text: message }] }),
});

// Resources for read-only data
server.registerResource({
  uri: "myapp://config",
  name: "App config",
  description: "Current app configuration",
  handler: async () => ({
    contents: [{ uri: "myapp://config", mimeType: "application/json", text: JSON.stringify({ theme: "dark" }) }],
  }),
});
```

Use **Zod** (or the SDK’s preferred schema format) for input validation so the model gets clear errors and the client gets typed parameters.

## Transport

- **stdio**: Default for Claude Desktop and many CLI clients. Start the server and connect over stdio.
- **HTTP/SSE**: For Cursor, cloud, or remote clients. Run an HTTP server that speaks the MCP protocol; separate the MCP server logic from the transport so you can switch.

Keep the **server logic independent** of transport (tools + resources), then plug in stdio or HTTP in the entrypoint.

## Best Practices

- **Schema first**: Define input schemas for every tool; document parameters and return shape.
- **Errors**: Return structured errors or messages the model can interpret; avoid raw stack traces in responses.
- **Idempotency**: Prefer idempotent tools where possible so retries are safe.
- **Rate and cost**: For tools that call external APIs, consider rate limits and cost; document in the tool description.
- **Versioning**: Pin SDK version in package.json; check release notes when upgrading (APIs change).

## Official SDKs and Docs

- **JavaScript/TypeScript**: `@modelcontextprotocol/sdk` (npm). Use Context7 with library name "MCP" or "model context protocol" for current docs.
- **Go**: Official Go SDK on GitHub (`modelcontextprotocol/go-sdk`).
- **C#**: Official C# SDK for .NET.

When in doubt, resolve the library ID for "MCP" or the specific SDK and run a query-docs call to get the latest registration and transport patterns.

## When to Use This Skill

Use when: implementing a new MCP server, adding tools or resources, choosing stdio vs HTTP, upgrading the SDK, or debugging MCP registration and transport issues.
