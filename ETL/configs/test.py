from redis import Redis

r = Redis()

r.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})
print(r.get("Bahamas"))