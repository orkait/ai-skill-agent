---
description: Middleware recipe
---

# Middleware

## Write a custom middleware

- Middleware to collect request count, statuses and uptime.
- Middleware to write custom `Server` header to the response.

### Server

```go reference
https://github.com/labstack/echox/blob/master/cookbook/middleware/server.go
```

### Response

#### Headers

```sh
Content-Length:122
Content-Type:application/json; charset=utf-8
Date:Thu, 14 Apr 2016 20:31:46 GMT
Server:Echo/3.0
```

#### Body

```js
{
  "uptime": "2016-04-14T13:28:48.486548936-07:00",
  "requestCount": 5,
  "statuses": {
    "200": 4,
    "404": 1
  }
}
```
