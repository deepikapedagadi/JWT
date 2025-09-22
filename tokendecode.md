Approach & Flow
1. User Registration

A user sends a POST request to /register with their email, name, and password.

The password is securely hashed using werkzeug.security.generate_password_hash.

A new User record is created in the PostgreSQL database using SQLAlchemy.

After successful registration, a JWT access token is generated and returned to the user.

2. User Login

A user logs in via a POST request to /login with their email and password.

The backend checks the user record in the database.

If the password matches (check_password_hash), a new JWT token is generated and sent back.

This token is the key to accessing protected routes.

3. Token Usage & Protection

The token must be sent in future requests using one of the following:

In the Authorization header: Bearer <token>

As a JSON body: { "token": "<token>" }

As a query parameter: ?token=<token>

Protected endpoints like /verify and (optionally) /users check for a valid JWT.

Token is verified using the app’s SECRET_KEY. If expired or tampered with, access is denied.

4. Token Decoding (Unverified)

The /decode endpoint allows clients to decode the JWT locally without verifying the signature.

This is useful for debugging or viewing token contents (header and payload).

5. Token Verification

The /verify endpoint checks if the token is:

Valid (correct signature)

Not expired

If verified, it returns token data; otherwise, it returns an error (e.g., expired or invalid token).

6. Refresh Token (Extension Ready)

The system is structured to easily support refresh tokens, allowing users to get a new access token without re-entering their credentials.
