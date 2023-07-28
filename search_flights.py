#!/usr/bin/env python
# coding: utf-8

# # API  Skyscanner Flights Search Engine

# In[37]:


import requests
import pandas as pd
import json

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
            iata = place_data.get('iata')
            return entity_id, iata

    return None, None

def search_flights(departure_date, return_date, origin, destination, adults, min_price, max_price, limit=5):
    origin_entity_id, origin_iata = search_city(origin)
    destination_entity_id, destination_iata = search_city(destination)
    
    if min_price:
        min_price = float(min_price)
    else:
        min_price = float('-inf')

    if max_price:
        max_price = float(max_price)
    else:
        max_price = float('-inf')

    if origin_entity_id is None:
        print(f"Origin city '{origin}' not found.")
        return None

    if destination_entity_id is None:
        print(f"Destination city '{destination}' not found.")
        return None

    url = "https://skyscanner-api.p.rapidapi.com/v3e/flights/live/search/synced"

    payload = {
        "query": {
            "market": "PT",
            "locale": "pt-PT",
            "currency": "EUR",
            "queryLegs": [
                {
                    "originPlaceId": {"iata": origin_iata},
                    "destinationPlaceId": {"iata": destination_iata},
                    "date": {
                        "year": int(departure_date.split('-')[0]),
                        "month": int(departure_date.split('-')[1]),
                        "day": int(departure_date.split('-')[2])
                    }
                },
                {
                    "originPlaceId": {"iata": destination_iata},
                    "destinationPlaceId": {"iata": origin_iata},
                    "date": {
                        "year": int(return_date.split('-')[0]),
                        "month": int(return_date.split('-')[1]),
                        "day": int(return_date.split('-')[2])
                    }
                }
            ],
            "cabinClass": "CABIN_CLASS_ECONOMY",
            "adults": adults,
            "childrenAges": [0]
        }
    }

    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "81d929c401msh55db1148647344cp1f1e2djsnd3e37a9caf26",
        "X-RapidAPI-Host": "skyscanner-api.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers)
    print("Response:", response.status_code)
    print("Response Content:", response.content)

    flight_details = []    
    
    min_price = float(min_price)
    max_price = float(max_price)
    
    if response.status_code == 200:
        itineraries = response.json().get("content", {}).get("results", {}).get("itineraries", {})
        if itineraries:
            flight_details = []
            for itinerary_id, itinerary_info in itineraries.items():
                pricing_options = itinerary_info.get("pricingOptions", [])
                for pricing_option in pricing_options:
                    price = pricing_option.get("price", {}).get("amount")
                    if price and min_price <= float(price) <= max_price:
                        outbound_date = departure_date
                        inbound_date = return_date
                        outbound_origin = origin
                        outbound_destination = destination
                        inbound_origin = destination
                        inbound_destination = origin

                        flight_details.append([
                            outbound_date,
                            outbound_origin,
                            outbound_destination,
                            inbound_date,
                            inbound_origin,
                            inbound_destination,
                            price
                        ])

    if flight_details:
        flight_df = pd.DataFrame(flight_details, columns=[
            "Outbound Date",
            "Outbound Origin",
            "Outbound Destination",
            "Inbound Date",
            "Inbound Origin",
            "Inbound Destination",
            "Price"
        ])
        flight_df["Outbound Date"] = pd.to_datetime(flight_df["Outbound Date"])
        flight_df["Inbound Date"] = pd.to_datetime(flight_df["Inbound Date"])

        if not flight_df.empty:
            flight_df["Outbound Date"] = pd.to_datetime(flight_df["Outbound Date"])
            flight_df["Inbound Date"] = pd.to_datetime(flight_df["Inbound Date"])

            return flight_df
        else:
            print("No flights found.")
            return pd.DataFrame()


# In[38]:


origin = "Lisbon"
destination = "Madrid"
departure_date = "2023-09-03"
return_date = "2023-09-12"
adults = 2
min_price = 50
max_price = 500

flight_df = search_flights(departure_date, return_date, origin, destination, adults, min_price, max_price)
sorted_flight_df = flight_df.sort_values("Price", ignore_index=True, ascending=True)

cheapest_flight = sorted_flight_df.head(1)
medium_index = len(sorted_flight_df) // 2
medium_flight = sorted_flight_df.iloc[[medium_index]]
expensive_flight = sorted_flight_df.tail(1)


# In[39]:


sorted_flight_df


# In[40]:


cheapest_flight


# In[41]:


medium_flight


# In[42]:


expensive_flight


# In[ ]:




