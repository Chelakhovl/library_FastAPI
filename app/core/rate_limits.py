from app.core.limiter import limiter


rate_get = limiter.limit("30/minute")


rate_mutate = limiter.limit("50/minute")
