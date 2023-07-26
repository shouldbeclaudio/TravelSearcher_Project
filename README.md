![97bf8ac4-c8a1-4bc1-811d-1d8d41459f5b](https://github.com/shouldbeclaudio/TravelSearcher_Project/assets/44953699/20a1627c-83db-4089-966b-fd530031d1e9)

# Travel Searcher App Guidance

- search_flights.py
- search_hotels.py
- app.py
- results.html

## Process 01

<details>
<summary><h2>def search_city</h2></summary>

  - In function city_name, i made a API connection to retrieve the IATA airport codes to be able to search for city names to merge
    with hotel search and make a unique search by city name

  -     entity_id = search_city(city_name)
  
</details>

<details>
<summary><h2>def search_flights</h2></summary>

   - In function search_flights, i made a API connection and made some setup's for flights search:

    if flight_details:
        flight_df = pd.DataFrame(flight_details, columns=[
            "Outbound Date",
            "Outbound Origin",
            "Outbound Destination",
            "Inbound Date",
            "Inbound Origin",
            "Inbound Destination",
            "Price"
     
</details>

<details>
<summary><h2>def search_hotels</h2></summary>

   - In function search_hotels, i made a API connection and made some setup's for hotels search:

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

</details>

## Process 02

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
            const bucketIndex = Math.ceil((item.Price - minPrice) / bucketSize);
            bucketCounts[bucketIndex]++;
         });

         const labels = bucketCounts.map((count, index) => {
            const bucketStart = minPrice + index * bucketSize;
            const bucketEnd = bucketStart + bucketSize;
            return `${bucketStart.toFixed(0)} - ${bucketEnd.toFixed(0)}`;
         });

         const ctx = document.getElementById(chartId).getContext('2d');
         const chosenBucketIndex = Math.floor((chosenPrice - minPrice) / bucketSize);



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

 
</details>


<details>
<summary><h2>Presentation</h2></summary>

![1](https://github.com/shouldbeclaudio/TravelSearcher_Project/assets/44953699/8f52c0d8-ffbe-4bb1-9ab3-88a9e08bfd3b)
![2](https://github.com/shouldbeclaudio/TravelSearcher_Project/assets/44953699/d473d13a-0d89-4572-8226-a0ae281e58ef)
![3](https://github.com/shouldbeclaudio/TravelSearcher_Project/assets/44953699/e889c84f-bb5f-4bbf-b84b-4d99bbfe3c09)
![4](https://github.com/shouldbeclaudio/TravelSearcher_Project/assets/44953699/bfeb53b4-d019-4d69-8375-44dcfb9f0b60)

</details>
