![97bf8ac4-c8a1-4bc1-811d-1d8d41459f5b](https://github.com/shouldbeclaudio/TravelSearcher_Project/assets/44953699/20a1627c-83db-4089-966b-fd530031d1e9)

# Travel Searcher App Guidance

- search_flights.py
- search_hotels.py
- app.py
- results.html

## Process #1

<details>
<summary><h2>search_city</h2></summary>

  - In function city_name, i made a API connection to retrieve the IATA airport codes to be able to search for city names to merge
    with hotel search and make a unique search by city name

  - def search_city "flight's"

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

    - def search_city "Hotel's"

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
      
  
</details>

<details>
<summary><h2>search_flights</h2></summary>

   - In function search_flights, i made a API connection and made some setup's for flights search:

    def search_flights(departure_date, return_date, origin, destination, adults, min_price, max_price, limit=5):
                       origin_entity_id, origin_iata = search_city(origin)
                       destination_entity_id, destination_iata = search_city(destination)

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
     
</details>

<details>
<summary><h2>search_hotels</h2></summary>

   - In function search_hotels, i made a API connection and made some setup's for hotels search:

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

</details>

## Process #2

<details>
<summary><h2>results.html</h2></summary>

  - Flight Search

            function sortFlightTable() {
            const flightTable = document.getElementById('flight-table');
            const sortOption = document.getElementById('flight-sort').value;
            const rows = Array.from(flightTable.getElementsByTagName('tr')).slice(1);
            rows.sort((a, b) => {
                const aPrice = parseFloat(a.getElementsByTagName('td')[6].innerText);
                const bPrice = parseFloat(b.getElementsByTagName('td')[6].innerText);
                if (sortOption === 'price-low-high') {
                    return aPrice - bPrice;
                } else {
                    return bPrice - aPrice;
                }
            });
            rows.forEach(row => flightTable.appendChild(row));
        }

   - Hotel Search

              function sortHotelTable() {
            const hotelTable = document.getElementById('hotel-table');
            const sortOption = document.getElementById('hotel-sort').value;
            const rows = Array.from(hotelTable.getElementsByTagName('tr')).slice(1);
            rows.sort((a, b) => {
                const aPrice = parseFloat(a.getElementsByTagName('td')[4].innerText);
                const bPrice = parseFloat(b.getElementsByTagName('td')[4].innerText);
                if (sortOption === 'price-low-high') {
                    return aPrice - bPrice;
                } else {
                    return bPrice - aPrice;
                }
            });
            rows.forEach(row => hotelTable.appendChild(row));

         }


   - Hotel Histogram

    function generateHotelPriceHistogram(data, chartId, chosenPrice) {
        const bucketSize = 30;
        const minPrice = Math.min(...data.map(item => item.Price));
        const maxPrice = Math.max(...data.map(item => item.Price));
    
        const bucketCounts = new Array(Math.ceil((maxPrice - minPrice) / bucketSize)).fill(0);

        data.forEach(item => {
            const bucketIndex = Math.ceil((item.Price - minPrice) / bucketSize); // Modified line
            bucketCounts[bucketIndex]++;
        });

        const labels = bucketCounts.map((count, index) => {
            const bucketStart = minPrice + index * bucketSize;
            const bucketEnd = bucketStart + bucketSize;
            return `${bucketStart.toFixed(0)} - ${bucketEnd.toFixed(0)}`;
        });

        const ctx = document.getElementById(chartId).getContext('2d');
        const chosenBucketIndex = Math.floor((chosenPrice - minPrice) / bucketSize); // Updated line

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Price',
                    data: bucketCounts,
                    backgroundColor: bucketCounts.map((count, index) => {
                        const bucketStart = minPrice + index * bucketSize;
                        const bucketEnd = bucketStart + bucketSize;
                        if (chosenPrice >= bucketStart && chosenPrice <= bucketEnd) {
                            return 'rgba(255, 0, 0, 0.7)';
                        } else {
                            return 'rgba(0, 0, 0, 0.7)';
                        }
                    }),
                    borderColor: 'black',
                    borderWidth: 1,
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        suggestedMax: Math.max(...bucketCounts) * 1.1,
                    },
                },
                plugins: {
                    legend: {
                        display: false,
                    },
                    annotation: {
                        annotations: [{
                            type: 'line',
                            mode: 'horizontal',
                            scaleID: 'y',
                            value: chosenPrice,
                            borderColor: 'red',
                            borderWidth: 2,
                            label: {
                                content: `Chosen Price: ${chosenPrice}`,
                                enabled: true,
                                position: 'right'
                            }
                        }]
                    }
                }
            }
        });
    }

        const hotelData = [];
        const hotelTable = document.getElementById('hotel-table');
        const hotelRows = hotelTable.getElementsByTagName('tr');
        for (let i = 1; i < hotelRows.length; i++) {
            const hotelColumns = hotelRows[i].getElementsByTagName('td');
            const hotelPrice = parseFloat(hotelColumns[4].innerText);
            hotelData.push({ Price: hotelPrice });
        }
    
        const chosenHotelPrice = Math.min(...hotelData.map(item => item.Price));
        generateHotelPriceHistogram(hotelData, 'hotel-prices-chart', chosenHotelPrice);



   - Flight Histogram

         function generateFlightPriceHistogram(data, chartId, chosenPrice) {
            const bucketSize = 80;
            const minPrice = Math.min(...data.map(item => item.Price));
            const maxPrice = Math.max(...data.map(item => item.Price));
            const bucketCounts = new Array(Math.ceil((maxPrice - minPrice) / bucketSize)).fill(0);
        
            data.forEach(item => {
                const bucketIndex = Math.floor((item.Price - minPrice) / bucketSize);
                bucketCounts[bucketIndex]++;
            });
        
            const labels = bucketCounts.map((count, index) => {
                const bucketStart = minPrice + index * bucketSize;
                const bucketEnd = bucketStart + bucketSize;
                return `${bucketStart.toFixed(0)} - ${bucketEnd.toFixed(0)}`;
            });
        
            const ctx = document.getElementById(chartId).getContext('2d');
        
            let chosenBucketIndex = Math.floor((chosenPrice - minPrice) / bucketSize);
            if (chosenBucketIndex < 0) {
                chosenBucketIndex = 0;
            } else if (chosenBucketIndex >= bucketCounts.length) {
                chosenBucketIndex = bucketCounts.length - 1;
            }
        
            const adjustedChosenPrice = minPrice + (chosenBucketIndex * bucketSize) + bucketSize / 2;
        
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Price',
                        data: bucketCounts,
                        backgroundColor: bucketCounts.map((count, index) => {
                            const bucketStart = minPrice + index * bucketSize;
                            const bucketEnd = bucketStart + bucketSize;
                            if (chosenPrice >= bucketStart && chosenPrice <= bucketEnd) {
                                return 'rgba(255, 0, 0, 0.7)';
                            } else {
                                return 'rgba(0, 0, 0, 0.7)';
                            }
                        }),
                        borderColor: 'black',
                        borderWidth: 1,
                    }],
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            suggestedMax: Math.max(...bucketCounts) * 1.1,
                        },
                    },
                    plugins: {
                        legend: {
                            display: false,
                        },
                        annotation: {
                            annotations: [{
                                type: 'line',
                                mode: 'horizontal',
                                scaleID: 'y',
                                value: adjustedChosenPrice,
                                borderColor: 'red',
                                borderWidth: 2,
                                label: {
                                    content: `Chosen Price: ${adjustedChosenPrice.toFixed(0)}`,
                                    enabled: true,
                                    position: 'right',
                                },
                            }],
                        },
                    },
                },
            });
         }
        
         const flightData = [];
         const flightTable = document.getElementById('flight-table');
         const flightRows = flightTable.getElementsByTagName('tr');
         for (let i = 1; i < flightRows.length; i++) {
            const flightColumns = flightRows[i].getElementsByTagName('td');
            const flightPrice = parseFloat(flightColumns[6].innerText);
            flightData.push({ Price: flightPrice });
         }
        
         const chosenFlightPrice = Math.min(...flightData.map(item => item.Price));
         generateFlightPriceHistogram(flightData, 'flight-prices-chart', chosenFlightPrice); 

 
</details>

<details>
<summary><h2>App Deploy</h2></summary>

- Terminal:
  
          ~ % cd Project
          ~ % python app.py

</details>

<details>
<summary><h2>App Flow Diagram</h2></summary>

<img width="710" alt="Captura de ecrã 2023-07-27, às 23 47 16" src="https://github.com/shouldbeclaudio/TravelSearcher_Project/assets/44953699/50625e02-4ec2-4db9-b40e-3048fd137b76">

</details>


<details>
<summary><h2>Presentation</h2></summary>

![1](https://github.com/shouldbeclaudio/TravelSearcher_Project/assets/44953699/7e0912c2-fa8c-402f-a628-3f648ec83ace)
![2](https://github.com/shouldbeclaudio/TravelSearcher_Project/assets/44953699/7f395a70-2a97-4c4d-ba6c-7b2d8d4d0605)
![3](https://github.com/shouldbeclaudio/TravelSearcher_Project/assets/44953699/c868c22c-738d-4744-ab65-6058024b0a50)
![4](https://github.com/shouldbeclaudio/TravelSearcher_Project/assets/44953699/608dc442-d595-4acc-85c9-5debfc5bde3a)
![5](https://github.com/shouldbeclaudio/TravelSearcher_Project/assets/44953699/b7669edb-e177-42c5-b083-a857cbb01e38)

</details>
