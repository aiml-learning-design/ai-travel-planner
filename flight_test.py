import http.client

conn = http.client.HTTPSConnection("sky-scrapper.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "54b3678a63mshe9d415607df25b9p17d896jsn5d5905243bd9",
    'x-rapidapi-host': "sky-scrapper.p.rapidapi.com"
}

conn.request("GET", "/api/v2/flights/searchFlightEverywhere?originEntityId=95673320&cabinClass=economy&journeyType=one_way&currency=USD", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))