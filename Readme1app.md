User logs in → server returns a short-lived access token and a long-lived refresh token.

Access token → sent in x-access-token header for protected APIs.

Refresh token → used at /refresh to get a new access token.

Errors → handled for missing, expired, or invalid tokens.

/protected → example route that requires a valid token.
