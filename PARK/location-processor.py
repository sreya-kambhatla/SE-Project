from flask import Flask, render_template, redirect, request, url_for
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from datetime import *
import json
import certifi
import atexit

app = Flask(__name__)

load_dotenv()
uri = os.getenv("MONGODB_ATLAS_URI")
client = MongoClient(uri, tlsCAFile=certifi.where())

@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/search', methods=['GET'])
def search():
    location = request.args.get('location')
    start_date = request.args.get('start-date')
    end_date = request.args.get('end-date')
    start_time = request.args.get('start-time')
    end_time = request.args.get('end-time')

    if start_date and end_date and start_time and end_time:
        park_start = f"{start_date} {start_time}"
        park_end = f"{end_date} {end_time}"
        day_of_week = datetime.strptime(start_date, "%Y-%m-%d").strftime("%A")
    else:
        park_start = datetime.now().strftime("%Y-%m-%d %H:%M")
        park_end = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        day_of_week = datetime.now().strftime("%A")

    if location:
        redirect_url = url_for('results', location=location, userEntry='True', park_start=park_start, park_end=park_end, day_of_week=day_of_week)
    else:
        default_location = 'New York, NY'
        redirect_url = url_for('results', location=default_location, userEntry='False', park_start=park_start, park_end=park_end, day_of_week=day_of_week)

    return redirect(redirect_url)

@app.route('/results')
def results():
    flask_location = request.args.get('location')
    user_entry = request.args.get('userEntry')
    park_start_str = request.args.get('park_start')
    park_end_str = request.args.get('park_end')
    print("PARK START: ", park_start_str)
    print("PARK END: ", park_end_str)
    day_of_week = request.args.get('day_of_week')

    time_start = datetime.strptime(park_start_str, "%Y-%m-%d %H:%M")
    time_end = datetime.strptime(park_end_str, "%Y-%m-%d %H:%M")

    # Extract time_start and time_end from park_start and park_end
    park_start = time_start.strftime("%H:%M")
    park_end = time_end.strftime("%H:%M")

    spots_n_prices = find_parking(park_start, park_end, day_of_week, time_start, time_end)
    parking_spots = spots_n_prices[0]
    prices = spots_n_prices[1]

    return render_template('results.html', flaskLocation=flask_location, userEntry=user_entry, parking_spots=parking_spots, prices=prices)

@app.route('/testimonials')
def testimonials():
    return render_template('testimonials.html')

@app.route('/subscriptions')
def subscriptions():
    return render_template('subscriptions.html')

@app.route('/app-page')
def app_page():
    return render_template('app-page.html')

@app.route('/about-us')
def about_us():
    return render_template('about-us.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

def find_parking(park_start, park_end, day_of_week, time_start, time_end):
    park_start = park_start
    park_end = park_end
    db = client['parkDB']
    collection = db['parking_locations']

    # Convert park_start and park_end to floats representing hours
    start_time_float = time_start.hour + time_start.minute / 100.0
    end_time_float = time_end.hour + time_end.minute / 100.0
    print("TIMES", start_time_float, end_time_float)

    # Calculate the duration in seconds
    time_duration = time_end - time_start
    time_duration_seconds = time_duration.total_seconds()

    start_query = 'openingHours.' + str(day_of_week) + '.start'
    end_query = 'openingHours.' + str(day_of_week) + '.end'
                    
    # Aggregation pipeline
    pipeline = [
    {
        '$match': {
            'openingDays': {'$in': ['all', day_of_week]}
        }
    },
    {
        '$match': {
            '$or': [
                {
                    '$and': [
                        {'openingHours.all.start': {'$lte': start_time_float}},
                        {'openingHours.all.end': {'$gte': end_time_float}}
                    ]
                },
                {
                    '$expr': {
                        '$and': [
                            {'$lte': [{'$ifNull': [f'${start_query}', 0]}, start_time_float]},
                            {'$gte': [{'$ifNull': [f'${end_query}', 24]}, end_time_float]}
                        ]
                    }
                }
            ]
        }
     }
    ]

    # Execute the aggregation pipeline
    results = list(collection.aggregate(pipeline))

    # Assuming pricing function exists and works with the combined results
    spots, prices = pricing(results, time_duration, day_of_week, start_time_float, end_time_float, time_duration_seconds)
    return spots, prices

def pricing(result, time_duration, day_of_week, park_start, park_end, time_duration_seconds):
    spots = []
    prices = []

    park_start = park_start
    park_end = park_end
    # Calculate hours and minutes
    hours, remainder = divmod(time_duration_seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    # Create a string representation
    time_duration_float = float(f"{int(hours):02d}.{int(minutes):02d}")
    # print(time_duration_str)

    count = 1
    for document in result:
        got_deal = False
        result_json = json.loads(json.dumps(document, default=str))
        print(count, "CHECK_IN: ", document.get('name'))
        count += 1

        # Declare main variables at the beginning
        # morning deal vars
        morning = result_json.get('prices', {}).get('specialPrice', {}).get('Morning', {})
        morning_prices = morning.get('price', {})
        morning_start = morning.get('start', [])
        morning_end = morning.get('end', [])

        # evening deal vars
        evening = result_json.get('prices', {}).get('specialPrice', {}).get('Evening', {})
        evening_prices = evening.get('price', {})
        evening_start = evening.get('start', [])
        evening_end = evening_prices.get('end', [])

        # flat rate vars
        flat_rate = result_json.get('prices', {}).get('specialPrice', {}).get('flatRate', {})
        flat_rate_prices = flat_rate.get('prices', {})

        # regular parking vars
        reg_park = result_json.get('prices', {}).get('byDay')
        reg_park_prices = reg_park.get('all', {})

        # check for flat rate
        if flat_rate_prices and day_of_week in flat_rate_prices:
            got_deal = True
            print("FLAT: ", result_json.get('name', ''))
            spots.append(result_json)
            prices.append(flat_rate_prices[day_of_week])

        # check for morning deal
        elif morning_prices and time_duration_seconds < 86400 and got_deal == False:
            print("in morning")
            print("MORNING PRICES LENGTH: ", len(morning_prices))
            if len(morning_prices) < 2:
                print("1 MORNING START IS", len(morning_start))
                if len(morning_start) < 1:
                    if park_start <= morning_start[0] and park_end <= morning_end[0]:
                        print(count, "MORNING 1: ", result_json.get('name', ''))
                        got_deal = True
                        spots.append(result_json)
                        prices.append(morning_prices.get('all'))
                        count += 1
                else:
                    print("2 MORNING START IS", len(morning_start))
                    if park_start >= morning_start[0] and park_start <= morning_start[1] and park_end <= morning_end[0]:
                        print(count, "MORNING 1.5: ", result_json.get('name', ''))
                        got_deal = True
                        spots.append(result_json)
                        prices.append(morning_prices.get('all'))
                        count += 1
            else:
                print("MORNING PRICE IS ", len(morning_prices))
                if len(morning_start) < 2:
                    print("3 MORNING START IS", len(morning_start))
                    if park_start <= morning_start[0] and park_end <= morning_end[0]:
                        print(count, "MORNING 2: ", result_json.get('name', ''))
                        got_deal = True
                        spots.append(result_json)
                        prices.append(morning_prices.get(f'{day_of_week}'))
                        count += 1
                else:
                    print(" 4 MORNING START IS", len(morning_start))
                    if park_start >= morning_start[0] and park_start <= morning_start[1] and park_end <= morning_end[0]:
                        print(count, "MORNING 2.5: ", result_json.get('name', ''))
                        got_deal = True
                        spots.append(result_json)
                        prices.append(morning_prices.get(f'{day_of_week}'))
                        count += 1

        # check for evening deal
        elif evening_prices and time_duration_seconds < 86400:
            print("in evening")
            if len(evening_prices) < 2:
                if park_start >= evening_start[0] and park_end <= evening_end[0] :
                    got_deal = True
                    print("EVENING 1: ", result_json.get('name', ''))
                    spots.append(result_json)
                    prices.append(morning_prices.get(f"{day_of_week}"))
            else:
                if park_start >= evening_start[0] and park_end <= evening_prices.get(f"{day_of_week}"):
                    got_deal = True
                    print("EVENING 2: ", result_json.get('name', ''))
                    spots.append(result_json)
                    prices.append(morning_prices.get(f"{day_of_week}"))


        # Regular parking prices
        elif got_deal == False:
            print("in regular")
            for hours in reg_park_prices:
                if time_duration_float <= float(hours):
                    print("REGULAR: ", result_json.get('name', ''))
                    spots.append(result_json)
                    prices.append(reg_park_prices.get(hours))
                    break

    return spots, prices

    
atexit.register(lambda: client.close())

if __name__ == '__main__':
    app.run(debug=True)
