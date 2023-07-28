from flask import Flask, render_template, request
from datetime import date
import pandas as pd
from search_flights import search_flights
from search_hotels import search_hotels

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():

    origin = request.form.get('origin')
    destination = request.form.get('destination')
    departure_date = request.form.get('departure_date')
    return_date = request.form.get('return_date')
    adults = int(request.form.get('adults'))
    min_price = request.form.get('min_price')
    max_price = request.form.get('max_price')

    flight_results = search_flights(departure_date, return_date, origin, destination, adults, min_price, max_price)

    inbound_date = date.fromisoformat(departure_date)
    outbound_date = date.fromisoformat(return_date)
    num_rooms = 1
    num_people = adults
    num_of_stays = (outbound_date - inbound_date).days
    hotel_results = search_hotels(destination, inbound_date, outbound_date, num_rooms, num_people, "PT", min_price, max_price)

    flight_data = flight_results if flight_results is not None else pd.DataFrame()
    hotel_data = pd.DataFrame()

    cheapest_flight = pd.DataFrame()
    medium_flight = pd.DataFrame()
    expensive_flight = pd.DataFrame()

    if flight_data.empty:
        flight_message = 'No flights found'
    else:
        sorted_flight_data = flight_data.sort_values("Price", ignore_index=True, ascending=True)
        cheapest_flight = sorted_flight_data.head(1)
        medium_index = len(sorted_flight_data) // 2
        medium_flight = sorted_flight_data.iloc[[medium_index]]
        expensive_flight = sorted_flight_data.tail(1)
        flight_message = None

    hotel_message = None
    cheapest_hotel = pd.DataFrame()
    medium_priced_hotel = pd.DataFrame()
    most_expensive_hotel = pd.DataFrame()

    if hotel_results is not None and 'content' in hotel_results and 'results' in hotel_results['content']:
        hotels = hotel_results['content']['results']['hotels']
        if hotels:
            all_results = []
            for hotel in hotels:
                name = hotel.get('name')
                stars = hotel.get('numberOfStars')
                price = hotel.get('priceInfo', {}).get('price')
                if price and max_price and int(price) > int(max_price):
                    continue
                result = {
                    'name': name,
                    'numberOfStars': stars,
                    'num_rooms': num_rooms,
                    'num_people': num_people,
                    'price': price if price else 'N/A'
                }
                all_results.append(result)

            hotel_data = pd.DataFrame(all_results)
            cheapest_hotel = hotel_data.sort_values("price", ignore_index=True, ascending=True).head(1)
            sorted_hotel_data = hotel_data.sort_values("price", ignore_index=True, ascending=False)
            medium_index = len(sorted_hotel_data) // 2
            medium_priced_hotel = sorted_hotel_data.iloc[[medium_index]]
            most_expensive_hotel = sorted_hotel_data.head(1)
        else:
            hotel_message = 'No hotels found'
    else:
        hotel_message = 'No hotels found'
    
    hotel_data['Price per Night'] = hotel_data['price']
    hotel_data['Total Price'] = hotel_data['price'] * num_of_stays
    
    max_price_numeric = float(max_price) if max_price else None

    if not flight_data.empty and not hotel_data.empty:

        all_combinations = pd.merge(flight_data.assign(key=1), hotel_data.assign(key=1), on='key').drop('key', axis=1)
        all_combinations['Price'] = pd.to_numeric(all_combinations['Price'])
        all_combinations['price'] = pd.to_numeric(all_combinations['price'])
        all_combinations['total_price'] = all_combinations['Price'] + (all_combinations['price'] * num_of_stays)
    
        cheapest_combination = all_combinations.nsmallest(1, 'total_price')
        cheapest_flight = cheapest_combination[['Outbound Date', 'Outbound Origin', 'Outbound Destination',
                                                'Inbound Date', 'Inbound Origin', 'Inbound Destination', 'Price']]
        cheapest_hotel = cheapest_combination[['name', 'numberOfStars', 'num_rooms', 'num_people', 'price']]
        
        all_combinations = all_combinations[all_combinations['total_price'] <= max_price_numeric]
        sorted_combinations = all_combinations.sort_values('total_price', ignore_index=True)
        
        medium_index = len(sorted_combinations) // 2

        if not sorted_combinations.empty and 0 <= medium_index < len(sorted_combinations):
           medium_combination = sorted_combinations.iloc[[medium_index]]
        else:
           medium_combination = None

        while not medium_combination.empty and medium_index < len(sorted_combinations) and medium_combination['total_price'].iloc[0] > max_price_numeric:
              medium_index += 1
              if medium_index >= len(sorted_combinations):
                 break
              medium_combination = sorted_combinations.iloc[[medium_index]]

        
        medium_flight = medium_combination[['Outbound Date', 'Outbound Origin', 'Outbound Destination',
                                            'Inbound Date', 'Inbound Origin', 'Inbound Destination', 'Price']]
        medium_priced_hotel = medium_combination[['name', 'numberOfStars', 'num_rooms', 'num_people', 'price']]

        star_ratings = [5.0, 4.0]
        expensive_combination = pd.DataFrame()

        for star_rating in star_ratings:

            combination_for_star_rating = all_combinations[
                all_combinations['numberOfStars'] == star_rating
            ]

            if not combination_for_star_rating.empty:
                
                most_expensive_for_star_rating = combination_for_star_rating.nlargest(1, 'total_price')
                
                if expensive_combination.empty or most_expensive_for_star_rating['total_price'].iloc[0] > expensive_combination['total_price'].iloc[0]:
                    expensive_combination = most_expensive_for_star_rating

        expensive_flight = expensive_combination[['Outbound Date', 'Outbound Origin', 'Outbound Destination',
                                                  'Inbound Date', 'Inbound Origin', 'Inbound Destination', 'Price']]
        expensive_hotel = expensive_combination[['name', 'numberOfStars', 'num_rooms', 'num_people', 'price']]

        if expensive_combination.empty:
            most_expensive_hotel = pd.DataFrame(columns=['name', 'numberOfStars', 'num_rooms', 'num_people', 'price'])
        else:
            most_expensive_hotel = expensive_hotel.copy()
            
    max_price_numeric = float(max_price) if max_price else None

    return render_template('results.html', flight_data=flight_data, hotel_data=hotel_data,
                           cheapest_flight=cheapest_flight, cheapest_hotel=cheapest_hotel,
                           medium_flight=medium_flight, medium_priced_hotel=medium_priced_hotel,
                           expensive_flight=expensive_flight, most_expensive_hotel=most_expensive_hotel, num_of_stays=num_of_stays)

if __name__ == '__main__':
    app.run(debug=True, port=8000)






# In[ ]:




