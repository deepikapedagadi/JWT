# JWT
Approach
1. Login → User sends username & password.
Server checks credentials.
If valid → creates:
Access Token(short life, e.g., 1 min).
Refresh Token(longer life, e.g., 1 hr).

2. Access APIs → User sends Access Token in `x-access-token` header.

   Server verifies token before allowing access.

3. Token Expiry → When access token expires, user can’t call protected APIs.

4. Refresh Token → User sends refresh token in `x-refresh-token` header.
Server validates it.
If valid → issues a new Access Token.

5. Re-login→ If refresh token is expired or invalid → user must login again.

This way:
Access Token = fast, short-lived key for APIs.
Refresh Token= backup key to get a new access token.


Impact of all three :
Access + Refresh → Secure and user-friendly.

JWT only → Secure but needs many logins.

Basic Auth → Not secure, bad for long use.
