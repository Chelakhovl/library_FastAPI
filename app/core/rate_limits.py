from app.core.limiter import limiter

# Декоратори-шорткати
rate_get = limiter.limit("60/minute")     # для публічних GET
rate_mutate = limiter.limit("10/minute") # для POST/PUT/DELETE/IMPORT
