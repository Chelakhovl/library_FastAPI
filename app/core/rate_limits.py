from app.core.limiter import limiter


rate_get = limiter.limit("60/minute")
rate_mutate = limiter.limit("10/minute")
