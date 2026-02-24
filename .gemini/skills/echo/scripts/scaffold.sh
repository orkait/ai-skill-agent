#!/bin/bash
# Echo Project Scaffold Generator
# Creates a new Echo project with sensible defaults and common patterns

set -e

PROJECT_NAME="${1:-my-echo-app}"
PORT="${2:-1323}"

echo "Creating Echo project: $PROJECT_NAME"

mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Initialize Go module
go mod init "$PROJECT_NAME"

# Create directory structure
mkdir -p {cmd/server,internal/{handlers,middleware,models},pkg,configs}

# Create main.go with graceful shutdown
cat > cmd/server/main.go <<'EOF'
package main

import (
    "context"
    "net/http"
    "os"
    "os/signal"
    "time"

    "github.com/labstack/echo/v4"
    "github.com/labstack/echo/v4/middleware"
)

func main() {
    e := echo.New()

    // Middleware
    e.Use(middleware.Logger())
    e.Use(middleware.Recover())
    e.Use(middleware.CORS())

    // Routes
    e.GET("/", func(c echo.Context) error {
        return c.JSON(http.StatusOK, map[string]string{
            "status": "healthy",
            "app": "MY_APP_NAME",
        })
    })

    e.GET("/health", func(c echo.Context) error {
        return c.JSON(http.StatusOK, map[string]string{"status": "ok"})
    })

    // Start server in goroutine
    go func() {
        if err := e.Start(":MY_PORT"); err != nil && err != http.ErrServerClosed {
            e.Logger.Fatal("shutting down the server")
        }
    }()

    // Wait for interrupt signal
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, os.Interrupt)
    <-quit
    e.Logger.Info("shutting down gracefully")

    // Graceful shutdown with 10s timeout
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    if err := e.Shutdown(ctx); err != nil {
        e.Logger.Fatal(err)
    }
}
EOF

# Replace placeholders
sed -i "s/MY_APP_NAME/$PROJECT_NAME/g" cmd/server/main.go
sed -i "s/MY_PORT/$PORT/g" cmd/server/main.go

# Create handler template
cat > internal/handlers/user.go <<'EOF'
package handlers

import (
    "net/http"
    "github.com/labstack/echo/v4"
)

type UserHandler struct{}

func NewUserHandler() *UserHandler {
    return &UserHandler{}
}

func (h *UserHandler) List(c echo.Context) error {
    // TODO: Implement list users
    return c.JSON(http.StatusOK, []map[string]interface{}{})
}

func (h *UserHandler) Get(c echo.Context) error {
    id := c.Param("id")
    // TODO: Implement get user
    return c.JSON(http.StatusOK, map[string]string{"id": id})
}

func (h *UserHandler) Create(c echo.Context) error {
    // TODO: Implement create user
    return c.JSON(http.StatusCreated, map[string]string{"status": "created"})
}

func (h *UserHandler) Update(c echo.Context) error {
    id := c.Param("id")
    // TODO: Implement update user
    return c.JSON(http.StatusOK, map[string]string{"id": id, "status": "updated"})
}

func (h *UserHandler) Delete(c echo.Context) error {
    id := c.Param("id")
    // TODO: Implement delete user
    return c.NoContent(http.StatusNoContent)
}
EOF

# Create custom middleware template
cat > internal/middleware/auth.go <<'EOF'
package middleware

import (
    "github.com/labstack/echo/v4"
    "net/http"
)

func Auth(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        token := c.Request().Header.Get("Authorization")
        
        if token == "" {
            return echo.NewHTTPError(http.StatusUnauthorized, "missing auth token")
        }
        
        // TODO: Implement token validation
        
        return next(c)
    }
}
EOF

# Create README
cat > README.md <<EOF
# $PROJECT_NAME

Echo framework web server

## Getting Started

\`\`\`bash
# Install dependencies
go mod download

# Run server
go run cmd/server/main.go

# Or build and run
go build -o bin/server cmd/server/main.go
./bin/server
\`\`\`

## API Endpoints

- \`GET /\` - Health check
- \`GET /health\` - Detailed health status

## Project Structure

\`\`\`
$PROJECT_NAME/
├── cmd/
│   └── server/          # Application entrypoint
├── internal/
│   ├── handlers/        # Request handlers
│   ├── middleware/      # Custom middleware
│   └── models/          # Data models
├── pkg/                 # Public libraries
└── configs/             # Configuration files
\`\`\`

## Development

### Adding a new route

1. Create handler in \`internal/handlers/\`
2. Register route in \`cmd/server/main.go\`
3. Add tests

### Environment Variables

- \`PORT\` - Server port (default: $PORT)
EOF

# Create Makefile
cat > Makefile <<EOF
.PHONY: run build test clean

run:
	go run cmd/server/main.go

build:
	go build -o bin/server cmd/server/main.go

test:
	go test ./... -v

clean:
	rm -rf bin/
EOF

# Create .gitignore
cat > .gitignore <<EOF
bin/
*.exe
*.test
.env
EOF

# Install dependencies
echo "Installing Echo..."
go get github.com/labstack/echo/v4
go get github.com/labstack/echo/v4/middleware

echo ""
echo "✅ Project created successfully!"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  go run cmd/server/main.go"
echo ""
echo "Server will start on http://localhost:$PORT"
