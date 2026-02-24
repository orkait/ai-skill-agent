---
description: Automatic TLS certificates from Let's Encrypt recipe
---

# Auto TLS

This recipe demonstrates how to obtain TLS certificates for a domain automatically from
Let's Encrypt. `Echo#StartAutoTLS` accepts an address which should listen on port `443`.

Browse to `https://<DOMAIN>`. If everything goes fine, you should see a welcome
message with TLS enabled on the website.

:::tip

- For added security you should specify host policy in auto TLS manager
- Cache certificates to avoid issues with rate limits (https://letsencrypt.org/docs/rate-limits) 
- To redirect HTTP traffic to HTTPS, you can use [redirect middleware](../middleware/redirect#https-redirect)

:::

## Server

```go reference
https://github.com/labstack/echox/blob/master/cookbook/auto-tls/server.go
```
