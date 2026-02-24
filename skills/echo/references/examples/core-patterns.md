# Echo Core Patterns — Code Examples

## Hello World Foundation

```go
package main

import (
    "github.com/labstack/echo/v4"
    "net/http"
)

func main() {
    e := echo.New()
    e.GET("/", func(c echo.Context) error {
        return c.String(http.StatusOK, "Hello, World!")
    })
    e.Logger.Fatal(e.Start(":1323"))
}
```

**Invariant**: Every handler receives `echo.Context` and returns `error`.

## Middleware Composition

```go
func ServerHeader(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        c.Response().Header().Set(echo.HeaderServer, "Echo/v4")
        return next(c)
    }
}

e.Use(ServerHeader)
api := e.Group("/api")
api.Use(middleware.Logger())
```

**Invariant**: Each middleware must call `next(c)` unless intentionally short-circuiting.

## REST API (CRUD)

```go
type User struct {
    ID   int    `json:"id"`
    Name string `json:"name"`
}

var users = map[int]*User{}
var seq = 1

e.POST("/users", func(c echo.Context) error {
    u := &User{ID: seq}
    if err := c.Bind(u); err != nil { return err }
    users[u.ID] = u
    seq++
    return c.JSON(http.StatusCreated, u)
})

e.GET("/users/:id", func(c echo.Context) error {
    id, _ := strconv.Atoi(c.Param("id"))
    return c.JSON(http.StatusOK, users[id])
})

e.PUT("/users/:id", func(c echo.Context) error {
    u := new(User)
    if err := c.Bind(u); err != nil { return err }
    id, _ := strconv.Atoi(c.Param("id"))
    users[id].Name = u.Name
    return c.JSON(http.StatusOK, users[id])
})

e.DELETE("/users/:id", func(c echo.Context) error {
    id, _ := strconv.Atoi(c.Param("id"))
    delete(users, id)
    return c.NoContent(http.StatusNoContent)
})
```

## WebSocket

```go
var upgrader = websocket.Upgrader{}

e.GET("/ws", func(c echo.Context) error {
    ws, err := upgrader.Upgrade(c.Response(), c.Request(), nil)
    if err != nil { return err }
    defer ws.Close()

    for {
        _, msg, err := ws.ReadMessage()
        if err != nil { break }
        if err = ws.WriteMessage(websocket.TextMessage, msg); err != nil { break }
    }
    return nil
})
```

**Invariant**: WebSocket hijacks the connection. Use `defer ws.Close()` always.

## Server-Sent Events (SSE)

```go
e.GET("/events", func(c echo.Context) error {
    w := c.Response()
    w.Header().Set("Content-Type", "text/event-stream")
    w.Header().Set("Cache-Control", "no-cache")
    w.Header().Set("Connection", "keep-alive")

    ticker := time.NewTicker(1 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-c.Request().Context().Done():
            return nil
        case t := <-ticker.C:
            fmt.Fprintf(w, "data: %s\n\n", t.Format(time.RFC3339))
            w.Flush()
        }
    }
})
```

**Critical**: Format is `data: <payload>\n\n`. Call `Flush()` after each event.

## JWT Authentication

```go
type jwtCustomClaims struct {
    Name  string `json:"name"`
    Admin bool   `json:"admin"`
    jwt.RegisteredClaims
}

e.POST("/login", func(c echo.Context) error {
    claims := &jwtCustomClaims{
        "Jon Snow", true,
        jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(72 * time.Hour)),
        },
    }
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    t, err := token.SignedString([]byte("secret"))
    if err != nil { return err }
    return c.JSON(http.StatusOK, map[string]string{"token": t})
})

r := e.Group("/restricted")
r.Use(echojwt.WithConfig(echojwt.Config{
    NewClaimsFunc: func(c echo.Context) jwt.Claims { return new(jwtCustomClaims) },
    SigningKey: []byte("secret"),
}))
```

## Graceful Shutdown

```go
go func() {
    if err := e.Start(":1323"); err != nil && err != http.ErrServerClosed {
        e.Logger.Fatal("shutting down the server")
    }
}()

quit := make(chan os.Signal, 1)
signal.Notify(quit, os.Interrupt)
<-quit

ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
defer cancel()
if err := e.Shutdown(ctx); err != nil {
    e.Logger.Fatal(err)
}
```

## Testing Pattern

```go
func TestHandler(t *testing.T) {
    e := echo.New()
    req := httptest.NewRequest(http.MethodGet, "/users/1", nil)
    rec := httptest.NewRecorder()
    c := e.NewContext(req, rec)
    c.SetParamNames("id")
    c.SetParamValues("1")

    if assert.NoError(t, getUser(c)) {
        assert.Equal(t, http.StatusOK, rec.Code)
    }
}
```
