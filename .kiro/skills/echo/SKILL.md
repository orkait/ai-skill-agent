---
name: echo
description: Build Go web servers with Echo framework — HTTP/2, WebSocket, SSE, JWT auth, file handling, TLS, middleware, proxying, and production patterns. Use when building Go HTTP servers or implementing web protocols.
triggers:
  - "Echo framework"
  - "Go web server"
  - "Go HTTP API"
  - "WebSocket Go"
  - "SSE Go"
  - "JWT Echo"
  - "Echo middleware"
  - "Go TLS server"
  - "graceful shutdown Go"
activation:
  mode: fuzzy
  priority: normal
  triggers:
    - "Echo framework"
    - "Go web server"
    - "Go HTTP API"
    - "WebSocket Go"
    - "SSE Go"
    - "JWT Echo"
    - "Echo middleware"
    - "Go TLS server"
    - "graceful shutdown Go"
compatibility: "Go 1.16+, Echo v4+"
metadata:
  version: "1.0.0"
references:
  - references/misc/introduction.md
  - references/examples/core-patterns.md
  - references/examples/cookbook-hello-world.md
  - references/examples/cookbook-crud.md
  - references/examples/cookbook-websocket.md
  - references/examples/cookbook-sse.md
  - references/examples/cookbook-jwt.md
  - references/examples/cookbook-cors.md
  - references/examples/cookbook-auto-tls.md
  - references/examples/cookbook-graceful-shutdown.md
  - references/examples/cookbook-file-upload.md
  - references/examples/cookbook-file-download.md
  - references/examples/cookbook-reverse-proxy.md
  - references/examples/cookbook-load-balancing.md
  - references/examples/cookbook-http2.md
  - references/examples/cookbook-http2-server-push.md
  - references/examples/cookbook-middleware.md
  - references/examples/cookbook-streaming-response.md
  - references/examples/cookbook-timeout.md
  - references/examples/cookbook-embed-resources.md
  - references/examples/cookbook-jsonp.md
  - references/examples/cookbook-subdomain.md
  - references/api/guide-quick-start.md
  - references/api/guide-routing.md
  - references/api/guide-request.md
  - references/api/guide-response.md
  - references/api/guide-binding.md
  - references/api/guide-error-handling.md
  - references/api/guide-testing.md
  - references/api/guide-static-files.md
  - references/api/guide-templates.md
  - references/api/guide-cookies.md
  - references/api/guide-customization.md
  - references/api/guide-ip-address.md
  - references/api/guide-start-server.md
  - references/patterns/middleware-logger.md
  - references/patterns/middleware-recover.md
  - references/patterns/middleware-cors.md
  - references/patterns/middleware-jwt.md
  - references/patterns/middleware-csrf.md
  - references/patterns/middleware-rate-limiter.md
  - references/patterns/middleware-basic-auth.md
  - references/patterns/middleware-key-auth.md
  - references/patterns/middleware-gzip.md
  - references/patterns/middleware-secure.md
  - references/patterns/middleware-session.md
  - references/patterns/middleware-body-limit.md
  - references/patterns/middleware-body-dump.md
  - references/patterns/middleware-request-id.md
  - references/patterns/middleware-proxy.md
  - references/patterns/middleware-redirect.md
  - references/patterns/middleware-rewrite.md
  - references/patterns/middleware-static.md
  - references/patterns/middleware-trailing-slash.md
  - references/patterns/middleware-context-timeout.md
  - references/patterns/middleware-method-override.md
  - references/patterns/middleware-casbin-auth.md
  - references/patterns/middleware-decompress.md
  - references/patterns/middleware-jaeger.md
  - references/patterns/middleware-prometheus.md
---

# Echo Framework Recipes

Comprehensive patterns for building production Go web servers with Echo framework.

## Core Structural Invariants

1. **Context envelope** — `echo.Context` wraps request/response for the entire lifecycle
2. **Middleware chain** — Composable interceptors with `next(c)` pass-through; each must call `next(c)` unless short-circuiting
3. **Protocol abstraction** — HTTP/1.1, HTTP/2, WebSocket, SSE share a unified interface
4. **Graceful degradation** — Features check capability and fall back (e.g., HTTP/2 push)
5. **Orthogonal features** — TLS, auth, routing, proxying are independent layers

---

## Quick Decision Matrix

| Need | Pattern | Reference |
|------|---------|-----------|
| REST API | CRUD handlers + JSON binding | `references/examples/cookbook-crud.md` |
| Real-time updates | SSE (server-push) | `references/examples/cookbook-sse.md` |
| Bidirectional real-time | WebSocket | `references/examples/cookbook-websocket.md` |
| Auth | JWT middleware | `references/examples/cookbook-jwt.md` |
| File upload | FormFile/MultipartForm | `references/examples/cookbook-file-upload.md` |
| File download | Attachment/Inline | `references/examples/cookbook-file-download.md` |
| TLS production | Auto TLS (Let's Encrypt) | `references/examples/cookbook-auto-tls.md` |
| TLS dev | Manual cert + HTTP/2 | `references/examples/cookbook-http2.md` |
| Proxy/LB | Proxy middleware | `references/examples/cookbook-reverse-proxy.md` |
| Production shutdown | Graceful shutdown + context timeout | `references/examples/cookbook-graceful-shutdown.md` |
| Chunked response | Streaming + Flush | `references/examples/cookbook-streaming-response.md` |
| Embedded assets | `//go:embed` + `http.FS` | `references/examples/cookbook-embed-resources.md` |

---

## Reference Index

### Cookbooks (working examples)
- Core patterns with code → `references/examples/core-patterns.md`
- Individual recipes → `references/examples/cookbook-*.md`

### Framework Guides (API reference)
- Routing, binding, request/response, error handling → `references/api/guide-*.md`

### Middleware
- Built-in and community middleware → `references/patterns/middleware-*.md`

---

## Execution Checklist

When implementing an Echo server:

1. **Define protocol** → HTTP/1.1, HTTP/2, WebSocket, SSE
2. **Security layer** → TLS config, CORS, JWT if needed
3. **Middleware chain order** → Logger → Recover → Auth → Custom
4. **Route structure** → Group by resource or subdomain
5. **Error handling** → Custom `HTTPErrorHandler` if needed
6. **Graceful shutdown** → Signal handling + context timeout
7. **Testing** → `httptest.NewRecorder()` for unit tests
8. **Deployment** → Reverse proxy (Nginx) or standalone with Auto TLS

---

## Common Pitfalls

### Middleware Order Matters
`Logger` must come before `Recover` so all requests are logged, including recovered panics.

### Context Goroutine Safety
`echo.Context` is not goroutine-safe. Copy values before launching goroutines.

### SSE Flushing
Must call `w.Flush()` after each write. Monitor `c.Request().Context().Done()` for client disconnect.

### WebSocket Lifecycle
Handler owns the connection loop after upgrade. Must manage cleanup with `defer ws.Close()`.

---

## When Echo Fits

- Need HTTP/2, WebSocket, SSE out of the box
- Want minimalist routing without reflection magic
- Prefer explicit middleware chains over implicit globals
- Building microservices or API gateways

## When to Consider Alternatives

- Need built-in ORM → Gin + GORM
- Want opinionated MVC structure → Beego
- Require extensive plugin ecosystem → Fiber
