# Celar Server

A FastAPI-based backend for the Celar social media platform. This server provides a REST API for user authentication, posts, and social interactions.

## Features

- **User Authentication**: JWT-based authentication with bcrypt password hashing
- **User Registration**: Create accounts with usernames, passwords, and software preferences (software prefences will be used in future features)
- **Posts**: Create and view image posts (base64 encoded)
- **Likes System**: Like/unlike posts with coin rewards
- **User Profiles**: View user information and coin counts
- **Demo Mode**: Optional demo mode

## Requirements

- Python 3.9+

## Installation

1. Clone the repository:
```bash
git clone https://github.com/simon0302010/celar.git
```

2. Navigate to the server directory:
```bash
cd server
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set the required environment variable:
```bash
export CELAR_KEY="your-secret-key-here"
```
> You can generate a key using Python: 
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

## Running the Server

```bash
python main.py
```
This runs the server on `http://0.0.0.0:8000` with auto-reload enabled.

### Demo Mode
```bash
python main.py demo
```
> Runs the server in demo mode (registration disabled).

### Dev Mode
```bash
python main.py dev
```
> Runs the server in development mode (auto reload enabled).

## API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication

Most endpoints require authentication via JWT Bearer tokens. Include the token in the Authorization header:

```
Authorization: Bearer your_jwt_token_here
```

### Endpoints

#### System Information

**GET `/details`**
- Returns server information
- No authentication required

Response:
```json
{
  "demo_mode": false,
  "version": "0.1.5"
}
```

#### User Management

**POST `/register`**
- Register a new user
- No authentication required

Request body:
```json
{
  "username": "john_doe",
  "password": "secure_password",
  "software": ["Python", "JavaScript", "Linux"]
}
```

Response:
```json
{
  "message": "User registered successfully"
}
```

**POST `/login`**
- Authenticate user and receive JWT token
- No authentication required

Request body:
```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

Response:
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

**GET `/profile`**
- Get current user's profile
- Requires authentication

Response:
```json
{
  "username": "john_doe",
  "software": ["Python", "JavaScript", "Linux"],
  "coins": 42
}
```

**GET `/profile/{username}`**
- Get another user's profile
- Requires authentication

Response:
```json
{
  "username": "jane_doe",
  "software": ["Go", "Docker", "macOS"],
  "coins": 15
}
```

**GET `/users`**
- Get list of all users
- Query parameters: `limit` (1-200, default: 50)
- Requires authentication

Response:
```json
[
  {
    "username": "john_doe",
    "software": ["Python", "JavaScript", "Linux"]
  },
  {
    "username": "jane_doe",
    "software": ["Go", "macOS"]
  }
]
```

#### Posts

**POST `/post`**
- Create a new post with image content
- Requires authentication

Request body:
```json
{
  "content": "base64_encoded_image_data"
}
```

Response:
```json
{
  "message": "Post created",
  "id": 123
}
```

**GET `/posts`**
- Get list of posts
- Query parameters: `limit` (1-200, default: 20)
- Requires authentication

Response:
```json
[
  {
    "id": 123,
    "author": "john_doe",
    "content": "base64_encoded_image_data",
    "created_at": "2025-10-04T12:00:00+00:00"
  }
]
```

#### Likes

**POST `/posts/{post_id}/like`**
- Like a post
- Requires authentication

Response:
```json
{
  "message": "Post liked"
}
```

**DELETE `/posts/{post_id}/like`**
- Unlike a post
- Requires authentication

Response:
```json
{
  "message": "Like removed"
}
```

**GET `/posts/{post_id}/likes`**
- Get like information for a post
- Requires authentication

Response:
```json
{
  "like_count": 5,
  "user_liked": true
}
```

**POST `/posts/{post_id}/like_toggle`**
- Toggle like status for a post
- Requires authentication

Response:
```json
{
  "like_count": 6,
  "user_liked": true
}
```

## Database Schema

The server uses SQLite with the following tables:

### Users
- `username` (TEXT, PRIMARY KEY): Unique username
- `password` (TEXT): Bcrypt hashed password
- `software` (TEXT): JSON array of software/technologies

### Posts
- `id` (INTEGER, PRIMARY KEY): Auto-incrementing post ID
- `author` (TEXT): Username of post creator
- `content` (BLOB): Base64 encoded image data
- `created_at` (TEXT): ISO format timestamp

### Post Likes
- `post_id` (INTEGER): Reference to post ID
- `username` (TEXT): Username who liked the post
- Primary key: (post_id, username)

## Error Handling

The API returns standard HTTP status codes:

- `200`: Success
- `400`: Bad Request (e.g., username already exists)
- `401`: Unauthorized (invalid/expired token)
- `404`: Not Found (user/post doesn't exist)

Error responses include details:
```json
{
  "detail": "Username already exists"
}
```

## Security Notes

- JWT tokens expire after 48 hours
- Passwords are hashed with bcrypt and salt
- Keep `CELAR_KEY` secret and secure
- Use HTTPS in production