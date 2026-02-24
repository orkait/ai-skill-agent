#!/bin/bash
# Echo Middleware Generator
# Creates common middleware patterns

MIDDLEWARE_TYPE="${1}"
OUTPUT_FILE="${2:-middleware.go}"

if [ -z "$MIDDLEWARE_TYPE" ]; then
    echo "Usage: ./generate-middleware.sh <type> [output-file]"
    echo ""
    echo "Available types:"
    echo "  request-id    - Add unique request ID to each request"
    echo "  rate-limit    - Basic rate limiting"
    echo "  metrics       - Request metrics collection"
    echo "  api-key       - API key authentication"
    echo "  request-log   - Detailed request logging"
    echo "  circuit-break - Circuit breaker pattern"
    exit 1
fi

case $MIDDLEWARE_TYPE in
    request-id)
        cat > "$OUTPUT_FILE" <<'EOF'
package middleware

import (
    "github.com/labstack/echo/v4"
    "github.com/google/uuid"
)

func RequestID(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        req := c.Request()
        res := c.Response()
        
        rid := req.Header.Get(echo.HeaderXRequestID)
        if rid == "" {
            rid = uuid.New().String()
        }
        
        res.Header().Set(echo.HeaderXRequestID, rid)
        c.Set("request_id", rid)
        
        return next(c)
    }
}
EOF
        echo "✅ Created request-id middleware in $OUTPUT_FILE"
        ;;

    rate-limit)
        cat > "$OUTPUT_FILE" <<'EOF'
package middleware

import (
    "github.com/labstack/echo/v4"
    "net/http"
    "sync"
    "time"
)

type RateLimiter struct {
    requests map[string][]time.Time
    mu       sync.RWMutex
    limit    int
    window   time.Duration
}

func NewRateLimiter(limit int, window time.Duration) *RateLimiter {
    rl := &RateLimiter{
        requests: make(map[string][]time.Time),
        limit:    limit,
        window:   window,
    }
    
    // Cleanup old entries periodically
    go func() {
        ticker := time.NewTicker(window)
        for range ticker.C {
            rl.cleanup()
        }
    }()
    
    return rl
}

func (rl *RateLimiter) Middleware(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        ip := c.RealIP()
        
        rl.mu.Lock()
        defer rl.mu.Unlock()
        
        now := time.Now()
        windowStart := now.Add(-rl.window)
        
        // Get requests for this IP
        requests := rl.requests[ip]
        
        // Filter requests within window
        var validRequests []time.Time
        for _, reqTime := range requests {
            if reqTime.After(windowStart) {
                validRequests = append(validRequests, reqTime)
            }
        }
        
        // Check limit
        if len(validRequests) >= rl.limit {
            return echo.NewHTTPError(http.StatusTooManyRequests, "rate limit exceeded")
        }
        
        // Add current request
        validRequests = append(validRequests, now)
        rl.requests[ip] = validRequests
        
        return next(c)
    }
}

func (rl *RateLimiter) cleanup() {
    rl.mu.Lock()
    defer rl.mu.Unlock()
    
    now := time.Now()
    windowStart := now.Add(-rl.window)
    
    for ip, requests := range rl.requests {
        var validRequests []time.Time
        for _, reqTime := range requests {
            if reqTime.After(windowStart) {
                validRequests = append(validRequests, reqTime)
            }
        }
        
        if len(validRequests) == 0 {
            delete(rl.requests, ip)
        } else {
            rl.requests[ip] = validRequests
        }
    }
}
EOF
        echo "✅ Created rate-limit middleware in $OUTPUT_FILE"
        echo "Usage: e.Use(NewRateLimiter(100, time.Minute).Middleware)"
        ;;

    metrics)
        cat > "$OUTPUT_FILE" <<'EOF'
package middleware

import (
    "github.com/labstack/echo/v4"
    "sync"
    "time"
)

type Metrics struct {
    mu             sync.RWMutex
    RequestCount   int64
    ErrorCount     int64
    TotalDuration  time.Duration
    StatusCodes    map[int]int64
}

func NewMetrics() *Metrics {
    return &Metrics{
        StatusCodes: make(map[int]int64),
    }
}

func (m *Metrics) Middleware(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        start := time.Now()
        
        err := next(c)
        
        duration := time.Since(start)
        status := c.Response().Status
        
        m.mu.Lock()
        m.RequestCount++
        m.TotalDuration += duration
        m.StatusCodes[status]++
        
        if err != nil || status >= 400 {
            m.ErrorCount++
        }
        m.mu.Unlock()
        
        return err
    }
}

func (m *Metrics) GetStats() map[string]interface{} {
    m.mu.RLock()
    defer m.mu.RUnlock()
    
    avgDuration := time.Duration(0)
    if m.RequestCount > 0 {
        avgDuration = m.TotalDuration / time.Duration(m.RequestCount)
    }
    
    statusCodesCopy := make(map[int]int64)
    for k, v := range m.StatusCodes {
        statusCodesCopy[k] = v
    }
    
    return map[string]interface{}{
        "request_count":    m.RequestCount,
        "error_count":      m.ErrorCount,
        "avg_duration_ms":  avgDuration.Milliseconds(),
        "status_codes":     statusCodesCopy,
    }
}
EOF
        echo "✅ Created metrics middleware in $OUTPUT_FILE"
        echo "Usage:"
        echo "  m := NewMetrics()"
        echo "  e.Use(m.Middleware)"
        echo "  e.GET(\"/metrics\", func(c echo.Context) error { return c.JSON(200, m.GetStats()) })"
        ;;

    api-key)
        cat > "$OUTPUT_FILE" <<'EOF'
package middleware

import (
    "github.com/labstack/echo/v4"
    "net/http"
)

type APIKeyValidator func(string) bool

func APIKey(validator APIKeyValidator) echo.MiddlewareFunc {
    return func(next echo.HandlerFunc) echo.HandlerFunc {
        return func(c echo.Context) error {
            key := c.Request().Header.Get("X-API-Key")
            
            if key == "" {
                key = c.QueryParam("api_key")
            }
            
            if key == "" {
                return echo.NewHTTPError(http.StatusUnauthorized, "missing API key")
            }
            
            if !validator(key) {
                return echo.NewHTTPError(http.StatusForbidden, "invalid API key")
            }
            
            return next(c)
        }
    }
}

// Example validator
func ValidateAPIKey(key string) bool {
    validKeys := map[string]bool{
        "secret-key-1": true,
        "secret-key-2": true,
    }
    return validKeys[key]
}
EOF
        echo "✅ Created api-key middleware in $OUTPUT_FILE"
        echo "Usage: e.Use(APIKey(ValidateAPIKey))"
        ;;

    request-log)
        cat > "$OUTPUT_FILE" <<'EOF'
package middleware

import (
    "github.com/labstack/echo/v4"
    "time"
)

func RequestLogger(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        req := c.Request()
        res := c.Response()
        
        start := time.Now()
        
        err := next(c)
        
        c.Logger().Infoj(map[string]interface{}{
            "time":       start.Format(time.RFC3339),
            "remote_ip":  c.RealIP(),
            "host":       req.Host,
            "method":     req.Method,
            "uri":        req.RequestURI,
            "user_agent": req.UserAgent(),
            "status":     res.Status,
            "latency_ms": time.Since(start).Milliseconds(),
            "bytes_out":  res.Size,
        })
        
        return err
    }
}
EOF
        echo "✅ Created request-log middleware in $OUTPUT_FILE"
        ;;

    circuit-break)
        cat > "$OUTPUT_FILE" <<'EOF'
package middleware

import (
    "github.com/labstack/echo/v4"
    "net/http"
    "sync"
    "time"
)

type CircuitBreaker struct {
    mu              sync.RWMutex
    failures        int
    lastFailureTime time.Time
    state           string // "closed", "open", "half-open"
    threshold       int
    timeout         time.Duration
}

func NewCircuitBreaker(threshold int, timeout time.Duration) *CircuitBreaker {
    return &CircuitBreaker{
        state:     "closed",
        threshold: threshold,
        timeout:   timeout,
    }
}

func (cb *CircuitBreaker) Middleware(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        cb.mu.Lock()
        
        // Check if circuit should move from open to half-open
        if cb.state == "open" && time.Since(cb.lastFailureTime) > cb.timeout {
            cb.state = "half-open"
            cb.failures = 0
        }
        
        // Reject if circuit is open
        if cb.state == "open" {
            cb.mu.Unlock()
            return echo.NewHTTPError(http.StatusServiceUnavailable, "circuit breaker open")
        }
        
        cb.mu.Unlock()
        
        // Execute request
        err := next(c)
        
        cb.mu.Lock()
        defer cb.mu.Unlock()
        
        if err != nil || c.Response().Status >= 500 {
            cb.failures++
            cb.lastFailureTime = time.Now()
            
            if cb.failures >= cb.threshold {
                cb.state = "open"
            }
        } else if cb.state == "half-open" {
            // Success in half-open state closes the circuit
            cb.state = "closed"
            cb.failures = 0
        }
        
        return err
    }
}
EOF
        echo "✅ Created circuit-break middleware in $OUTPUT_FILE"
        echo "Usage: e.Use(NewCircuitBreaker(5, 30*time.Second).Middleware)"
        ;;

    *)
        echo "❌ Unknown middleware type: $MIDDLEWARE_TYPE"
        echo "Available types: request-id, rate-limit, metrics, api-key, request-log, circuit-break"
        exit 1
        ;;
esac
