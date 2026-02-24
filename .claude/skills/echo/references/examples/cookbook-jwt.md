---
description: JWT recipe
---

# JWT

[JWT middleware](../middleware/jwt.md) configuration can be found [here](../middleware/jwt.md#configuration).

This is cookbook for:
- JWT authentication using HS256 algorithm.
- JWT is retrieved from `Authorization` request header.

## Server

### Using custom claims

```go reference
https://github.com/labstack/echox/blob/master/cookbook/jwt/custom-claims/server.go
```

### Using a user-defined KeyFunc

```go reference
https://github.com/labstack/echox/blob/master/cookbook/jwt/user-defined-keyfunc/server.go
```

## Client

### Login

Login using username and password to retrieve a token.

```sh
curl -X POST -d 'username=jon' -d 'password=shhh!' localhost:1323/login
```

### Response

```js
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE0NjE5NTcxMzZ9.RB3arc4-OyzASAaUhC2W3ReWaXAt_z2Fd3BN4aWTgEY"
}
```

### Request

Request a restricted resource using the token in `Authorization` request header.

```sh
curl localhost:1323/restricted -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE0NjE5NTcxMzZ9.RB3arc4-OyzASAaUhC2W3ReWaXAt_z2Fd3BN4aWTgEY"
```

### Response

```sh
Welcome Jon Snow!
```
