# API Documentation

## Auth

### JWT Token 

#### Payload
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "exp": 1705312200,
  "iat": 1705308600
}
```
#### Config
```
accessToken - 1h until expired
refreshToken - 30d until expired
```

### POST /auth/register

Регистрация нового пользователя. После успешной регистрации клиент редиректит на страницу входа.

**Request:**
```json
{
  "name": "Иван Петров",
  "email": "ivan@example.com",
  "password": "secret123"
}
```

**Response 201:** No Content

**Response 409:**
```json
{
  "error": "USER_EXISTS",
  "message": "Пользователь с таким email уже существует"
}
```

---

### POST /auth/login

**Request:**
```json
{
  "email": "ivan@example.com",
  "password": "secret123"
}
```

**Response 200:**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Иван Петров",
    "email": "ivan@example.com"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response 401:**
```json
{
  "error": "INVALID_CREDENTIALS",
  "message": "Неверный email или пароль"
}
```

---

### POST /auth/refresh

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response 401:**
```json
{
  "error": "INVALID_TOKEN",
  "message": "Токен недействителен или истёк"
}
```

---

### POST /auth/logout

@Auth

**Response 204:** No Content

---

## Users

### GET /users/me

@Auth

Получение своего пользователя

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Иван Петров",
  "email": "ivan@example.com"
}
```

---
### GET /users/search?q={query}

@Auth

Поиск пользователей по имени или email для шаринга. Возвращает до 10 результатов, исключая текущего пользователя. При пустом query возвращаем всех пользователей.

**Query params:**
- `q` (string, required) - поисковый запрос

**Response 200:**
```json
{
  "users": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Мария Сидорова",
      "email": "maria@example.com"
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "name": "Алексей Марин",
      "email": "alex.marin@example.com"
    }
  ]
}
```

---

## Desks

### POST /desks

@Auth

Создать новую доску.

**Request:**
```json
{
  "name": "Мой проект"
}
```

**Response 201:**
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440000",
  "name": "Мой проект",
  "owner_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-15T12:00:00Z",
  "updated_at": "2025-01-15T12:00:00Z"
}
```

---

### GET /desks

@Auth

Получить список своих досок. По умолчанию возвращаем макс. 5 шт.

**Query params:**
- `limit` (int, optional) — кол-во записей, по умолчанию 5, макс 100
- `offset` (int, optional) — смещение, по умолчанию 0

**Response 200:**
```json
{
  "desks": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440000",
      "name": "Мой проект",
      "owner_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2025-01-15T12:00:00Z",
      "updated_at": "2025-01-15T14:30:00Z"
    }
  ],
  "total": 42
}
```

---

### GET /desks/shared

@Auth

Получить список досок, к которым нам дали доступ. По умолчанию возвращаем макс. 5 шт.

**Query params:**
- `limit` (int, optional) - кол-во записей, по умолчанию 5, макс 100
- `offset` (int, optional) - смещение, по умолчанию 0

**Response 200:**
```json
{
  "desks": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440000",
      "name": "Командный проект",
      "owner": {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "Мария Сидорова"
      },
      "shared_at": "2025-01-15T13:00:00Z",
      "created_at": "2025-01-14T09:00:00Z",
      "updated_at": "2025-01-15T14:00:00Z"
    }
  ],
  "total": 15
}
```

---

### PATCH /desks/{desk_id}

@Auth

Обновить доску. Только для владельца.

**Request:**
```json
{
  "name": "Новое название"
}
```

**Response 200:**
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440000",
  "name": "Новое название",
  "owner_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-15T12:00:00Z",
  "updated_at": "Date.now()"
}
```

---

### DELETE /desks/{desk_id}

@Auth

Удалить доску. Только для владельца. Удаляет все стикеры и доступы.

**Response 204:** No Content

---

## Desk Sharing

### GET /desks/{desk_id}/shares

@Auth

Получить список пользователей с доступом к доске. Только для владельца.

**Response 200:**
```json
{
  "shares": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440000",
      "user": {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "Мария Сидорова",
        "email": "maria@example.com"
      },
      "created_at": "2025-01-15T13:00:00Z"
    }
  ]
}
```

---

### POST /desks/{desk_id}/shares

@Auth

Дать доступ пользователю к доске. Только для владельца.

**Request:**
```json
{
  "user_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Response 201:**
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440000",
  "user": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Мария Сидорова",
    "email": "maria@example.com"
  },
  "created_at": "2025-01-15T13:00:00Z"
}
```

**Response 409:**
```json
{
  "error": "ALREADY_SHARED",
  "message": "Пользователь уже имеет доступ к доске"
}
```

---

### DELETE /desks/{desk_id}/shares/{user_id}

@Auth

Отозвать доступ пользователя к доске. Только для владельца.

**Response 204:** No Content

---

## WebSocket - работа с доской

**URL:** `ws://localhost:8080/ws/desks/{desk_id}?token={access_token}`

### При подключении - текущее состояние доски

```json
{
  "event": "desk:init",
  "data": {
    "stickers": [
      {
        "id": "uuid",
        "coord": {"x": 100, "y": 200},
        "size": {"width": 150, "height": 100},
        "color": "#FFEB3B",
        "text": "Привет"
      }
    ]
  }
}
```

### Client → Server: создать стикер

```json
{
  "event": "sticker:create",
  "data": {
    "user_id": "660e8400-e29b-41d4-a716-446655440001",
    "coord": {"x": 100, "y": 200},
    "size": {"width": 150, "height": 100},
    "color": "#FFEB3B",
    "text": ""
  }
}
```

### Broadcast: стикер создан

```json
{
  "event": "sticker:created",
  "data": {
    "temp_id": "client-generated-uuid",
    "sticker": {
      "id": "server-uuid",
      "coord": {"x": 100, "y": 200},
      "size": {"width": 150, "height": 100},
      "color": "#FFEB3B",
      "text": ""
    }
  }
}
```

### Client → Server: обновить стикер

```json
{
  "event": "sticker:update",
  "data": {
    "sticker_id": "uuid",
    "coord": {"x": 150, "y": 250},
    "size": {"width": 200, "height": 150},
    "color": "#4CAF50",
    "text": "Текст"
  }
}
```

### Broadcast: стикер обновлён

```json
{
  "event": "sticker:updated",
  "data": {
    "sticker_id": "uuid",
    "coord": {"x": 150, "y": 250},
    "size": {"width": 200, "height": 150},
    "color": "#4CAF50",
    "text": "Текст"
  }
}
```

### Client → Server: удалить стикер

```json
{
  "event": "sticker:delete",
  "data": {
    "sticker_id": "uuid"
  }
}
```

### Broadcast: стикер удалён

```json
{
  "event": "sticker:deleted",
  "data": {
    "sticker_id": "uuid"
  }
}
```

### Ошибка

```json
{
  "event": "error",
  "data": {
    "code": "PERMISSION_DENIED",
    "message": "Нет доступа"
  }
}
```

---

## Коды ошибок

| Код | HTTP | Описание |
|-----|------|----------|
| `VALIDATION_ERROR` | 400 | Невалидные данные |
| `INVALID_CREDENTIALS` | 401 | Неверный email или пароль |
| `INVALID_TOKEN` | 401 | Токен недействителен |
| `FORBIDDEN` | 403 | Нет прав на действие |
| `NOT_FOUND` | 404 | Ресурс не найден |
| `EMAIL_EXISTS` | 409 | Email уже зарегистрирован |
| `ALREADY_SHARED` | 409 | Доступ уже выдан |
