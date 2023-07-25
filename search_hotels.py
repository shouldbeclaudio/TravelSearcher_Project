#!/usr/bin/env python
# coding: utf-8

# # Search Hotels API

# In[9]:


import requests
import json
import pandas as pd
from datetime import date

def search_city(city_name):
    url = "https://skyscanner-api.p.rapidapi.com/v3/geo/hierarchy/flights/en-US"

    headers = {
        "X-RapidAPI-Key": "81d929c401msh55db1148647344cp1f1e2djsnd3e37a9caf26",
        "X-RapidAPI-Host": "skyscanner-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    data = json.loads(response.text)

    places = data['places']

    for place_id, place_data in places.items():
        if place_data['name'].lower() == city_name.lower():
            entity_id = place_id
            return entity_id

    return None



def search_hotels(city_name, inbound_date, outbound_date, num_rooms, num_people, market, min_price=None, max_price=None, limit=None):
    entity_id = search_city(city_name)

    if entity_id is None:
        print("City not found.")
        return None

    url = "https://skyscanner-api.p.rapidapi.com/v3e/hotels/live/search/create"

    payload = {
        "query": {
            "market": "PT",
            "locale": "pt-PT",
            "currency": "EUR",
            "adults": num_people,
            "placeId": {"entityId": entity_id},
            "checkInDate": {
                "year": inbound_date.year,
                "month": inbound_date.month,
                "day": inbound_date.day
            },
            "checkOutDate": {
                "year": outbound_date.year,
                "month": outbound_date.month,
                "day": outbound_date.day
            },
            "rooms": num_rooms,
            "sortBy": "RELEVANCE_DESC"
        }
    }

    if min_price is not None:
        payload["query"]["priceRange"] = {"min": min_price}
    if max_price is not None:
        payload["query"]["priceRange"] = {"max": max_price}
    if min_price is not None and max_price is not None:
        payload["query"]["priceRange"] = {"min": min_price, "max": max_price}

    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "81d929c401msh55db1148647344cp1f1e2djsnd3e37a9caf26",
        "X-RapidAPI-Host": "skyscanner-api.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = json.loads(response.text)

    if limit is not None and len(data["content"]["results"]["hotels"]) > limit:
        data["content"]["results"]["hotels"] = data["content"]["results"]["hotels"][:limit]

    return data


# In[12]:


city_name = "Madrid"
inbound_date = date(2023, 9, 3)
outbound_date = date(2023, 9, 12)
num_rooms = 1
num_people = 2
min_price = 50
max_price = 500

results = search_hotels(city_name, inbound_date, outbound_date, num_rooms, num_people, "PT", min_price, max_price)

if results is not None:
    content = results.get('content', {})
    hotels = content.get('results', {}).get('hotels', [])
    all_results = [
    {
        'name': hotel['name'],
        'numberOfStars': hotel['numberOfStars'],
        'num_rooms': num_rooms,
        'num_people': num_people,
        'price': hotel.get('priceInfo', {}).get('price')
    }
    for hotel in hotels
]

    for hotel in hotels:
        name = hotel.get('name')
        stars = hotel.get('numberOfStars')
        price = hotel.get('priceInfo', {}).get('price')
        result = {
            'name': name,
            'numberOfStars': stars,
            'num_rooms': num_rooms,
            'num_people': num_people,
            'price': price if price else 'N/A'
        }
        all_results.append(result)

    hotel_results = pd.DataFrame(all_results)
    hotel_results_sorted = hotel_results.sort_values('price')

    medium_hotel_index = len(hotel_results_sorted) // 2
    cheapest_hotel = hotel_results_sorted.head(1)
    medium_hotel = hotel_results_sorted.iloc[[medium_hotel_index]]
    expensive_hotel = hotel_results_sorted.tail(1)


# In[13]:


hotel_results_sorted


# In[14]:


cheapest_hotel


# In[15]:


medium_hotel


# In[16]:


expensive_hotel


# In[ ]:




