---
description: CRUD (Create, read, update and delete) recipe
---

# CRUD

## Server

```go reference
https://github.com/labstack/echox/blob/master/cookbook/crud/server.go
```

## Client

### Create user

#### Request

```sh
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{"name":"Joe Smith"}' \
  localhost:1323/users
```

#### Response

```js
{
  "id": 1,
  "name": "Joe Smith"
}
```

### Get user

#### Request

```sh
curl localhost:1323/users/1
```

#### Response

```js
{
  "id": 1,
  "name": "Joe Smith"
}
```

### Update user

#### Request

```sh
curl -X PUT \
  -H 'Content-Type: application/json' \
  -d '{"name":"Joe"}' \
  localhost:1323/users/1
```

#### Response

```js
{
  "id": 1,
  "name": "Joe"
}
```

### Delete user

#### Request

```sh
curl -X DELETE localhost:1323/users/1
```

#### Response

`NoContent - 204`
