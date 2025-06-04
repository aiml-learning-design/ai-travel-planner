import http.client


conn = http.client.HTTPSConnection("sky-scrapper.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "54b3678a63mshe9d415607df25b9p17d896jsn5d5905243bd9",
    'x-rapidapi-host': "sky-scrapper.p.rapidapi.com"
}

conn.request("GET", "/api/v1/hotels/searchDestinationOrHotel?query=new", headers=headers)

res = conn.getresponse()
data = res.read()
print(f"--------DATA is-------------{data}")
#entity_Id = data.entityId

print(data.decode("utf-8"))


headers = {
    'x-rapidapi-key': "54b3678a63mshe9d415607df25b9p17d896jsn5d5905243bd9",
    'x-rapidapi-host': "sky-scrapper.p.rapidapi.com"
}

conn.request("GET", "/api/v1/hotels/searchHotels?entityId=101&checkin=2025-06-02&checkout=2025-06-06&adults=1&rooms=1&limit=30&sorting=-relevance&currency=USD&market=en-US&countryCode=US", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))