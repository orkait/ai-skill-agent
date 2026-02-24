# Echo Recipes Skill

A comprehensive Kiro skill for building production-ready web servers with the Echo framework in Go.

## Overview

This skill provides patterns, examples, and utilities for implementing:

- HTTP/1.1, HTTP/2, WebSocket, and SSE protocols
- JWT authentication and CORS configuration
- File upload/download handling
- Graceful shutdown and production deployment
- Reverse proxy and load balancing
- Custom middleware patterns
- TLS configuration including Let's Encrypt

## Installation

### Workspace Skill (Project-specific)
```bash
mkdir -p .kiro/skills
cp -r echo-recipes .kiro/skills/
```

### Global Skill (Available everywhere)
```bash
mkdir -p ~/.kiro/skills
cp -r echo-recipes ~/.kiro/skills/
```

## Structure

```
echo-recipes/
├── SKILL.md              # Main skill definition and patterns
├── README.md             # This file
├── scripts/
│   ├── scaffold.sh       # Generate new Echo project
│   └── generate-middleware.sh  # Generate middleware templates
└── references/           # Complete Echo documentation (59 files)
    ├── introduction.md                # Framework overview
    ├── cookbook-*.md                  # 20 cookbook examples
    ├── guide-*.md                     # 13 framework guides
    └── middleware-*.md                # 25 middleware docs
```

**Naming Convention**: Reference files use prefixes (`cookbook-`, `guide-`, `middleware-`) to organize documentation in a flat structure as per Kiro skill standards.

## Quick Start

### Using the Scaffold Script

Create a new Echo project with sensible defaults:

```bash
./scripts/scaffold.sh my-api 8080
cd my-api
go run cmd/server/main.go
```

This generates:
- Project structure with handlers, middleware, models
- Main server with graceful shutdown
- Health check endpoints
- Makefile and README
- Go module initialization

### Generating Middleware

Create common middleware patterns:

```bash
# Rate limiting
./scripts/generate-middleware.sh rate-limit internal/middleware/ratelimit.go

# Request metrics
./scripts/generate-middleware.sh metrics internal/middleware/metrics.go

# API key authentication
./scripts/generate-middleware.sh api-key internal/middleware/apikey.go

# Circuit breaker
./scripts/generate-middleware.sh circuit-break internal/middleware/circuit.go

# Request ID
./scripts/generate-middleware.sh request-id internal/middleware/requestid.go

# Detailed logging
./scripts/generate-middleware.sh request-log internal/middleware/logger.go
```

## Key Patterns Covered

### Protocol Implementations
- REST APIs (CRUD operations)
- WebSocket (bidirectional real-time)
- Server-Sent Events (server-push updates)
- HTTP/2 with server push
- Streaming responses

### Security
- JWT authentication with custom claims
- CORS configuration (allowlist and dynamic)
- Auto TLS with Let's Encrypt
- API key middleware
- Rate limiting

### File Operations
- Single and multiple file uploads
- File download (attachment vs inline)
- Embedded resources (Go 1.16+)

### Production Patterns
- Graceful shutdown with signal handling
- Reverse proxy and load balancing
- Request timeouts
- Circuit breaker pattern
- Request metrics and monitoring

## Activation

The skill activates automatically when you ask Kiro about:
- Building Go HTTP servers
- Implementing web protocols (WebSocket, SSE, HTTP/2)
- Setting up authentication or CORS
- File handling in web servers
- Production deployment patterns

Example queries:
- "Create an Echo server with JWT auth"
- "How do I implement WebSocket with Echo?"
- "Set up graceful shutdown for my Go server"
- "Add rate limiting middleware"
- "Configure CORS for multiple origins"

## Reference Documentation

The `references/` directory contains 59 comprehensive documentation files from the official Echo framework, organized with prefixed filenames:

### Categories

**Introduction** (1 file)
- `introduction.md` - Framework overview and core concepts

**Cookbook Examples** (20 files with `cookbook-` prefix)
- Complete working examples: auto-tls, cors, crud, embed-resources, file-download, file-upload, graceful-shutdown, hello-world, http2, http2-server-push, jsonp, jwt, load-balancing, middleware, reverse-proxy, sse, streaming-response, subdomain, timeout, websocket

**Framework Guides** (13 files with `guide-` prefix)
- Core concepts and usage: binding, cookies, customization, error-handling, ip-address, quick-start, request, response, routing, start-server, static-files, templates, testing

**Middleware Documentation** (25 files with `middleware-` prefix)
- Built-in and community middleware: basic-auth, body-dump, body-limit, casbin-auth, context-timeout, cors, csrf, decompress, gzip, jaeger, jwt, key-auth, logger, method-override, prometheus, proxy, rate-limiter, recover, redirect, request-id, rewrite, secure, session, static, trailing-slash

All references include practical examples and implementation details. See `SKILL.md` for the complete categorized listing.

## Best Practices

The skill emphasizes:

1. **Structural invariants** over implementation details
2. **Middleware composition** for cross-cutting concerns
3. **Graceful degradation** for optional features
4. **Explicit error handling** over silent failures
5. **Resource cleanup** with defer patterns
6. **Context awareness** for cancellation and timeouts

## Requirements

- Go 1.16 or higher
- Echo v4 or higher (`github.com/labstack/echo/v4`)

## License

This skill packages official Echo framework examples and patterns.
Original Echo framework: MIT License
Skill packaging: MIT License

## Additional Resources

- Echo Official Docs: https://echo.labstack.com
- Echo Source: https://github.com/labstack/echo
- Echo Cookbook: https://github.com/labstack/echox/tree/master/cookbook
- Community Middleware: https://github.com/labstack/echo-contrib
