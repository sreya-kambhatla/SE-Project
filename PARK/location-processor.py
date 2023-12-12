from flask import Flask, render_template, redirect, request, url_for, session
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from datetime import *
import json


app = Flask(__name__)
app.secret_key = os.urandom(24)

load_dotenv()
uri = os.getenv("MONGODB_ATLAS_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

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
    userEntry = request.args.get('userEntry')
    park_start_str = request.args.get('park_start')
    park_end_str = request.args.get('park_end')
    day_of_week = request.args.get('day_of_week')

    park_start = datetime.strptime(park_start_str, "%Y-%m-%d %H:%M")
    park_end = datetime.strptime(park_end_str, "%Y-%m-%d %H:%M")

    find_parking(park_start, park_end, day_of_week)
    return render_template('results.html', flaskLocation=flask_location, userEntry=userEntry)

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

def find_parking(park_start, park_end, day_of_week):
    collection = client.get_database("parkDB").parking_locations

    park_start = park_start
    park_end = park_end
    day_of_week = day_of_week
    start_time_str = park_start.strftime("%H:%M")
    end_time_str = park_end.strftime("%H:%M")

    time_duration = park_end - park_start
    time_duration_seconds = time_duration.total_seconds()

    # End times that are less than start times are considered to be the
    # next day, and 24 has been added to their value to account for that.
    pipeline = [
        {
            "$match": {
                "openingDays": {
                    "$in": ["all", day_of_week]  # Filters for 'all' or specific day of the week
                }
            }
        },
        {
            "$match": {
                "$or": [
                    {
                        "$and": [
                            {"openingHours.all.start": {"$lte": start_time_str}},
                            {"openingHours.all.end": {"$gte": end_time_str}}
                        ]
                    },
                    {
                        "$and": [
                            {f"openingHours.{day_of_week}.start": {"$lte": start_time_str}},
                            {f"openingHours.{day_of_week}.end": {"$gte": end_time_str}}
                        ]
                    }
                ]
            }
        },
        {
            "$match": {
                "$or": [
                    {"$expr": {"$lt": ["$time_elapsed_hours", "24:00"]}},  # Checks if time elapsed is less than 24 hours
                    {"prices.byDay.all.24:00": {"$exists": True}}  # Checks if 24-hour pricing exists
                ]
            }
        }
    ]
    result = list(collection.aggregate(pipeline))
    pricing(result, time_duration, day_of_week, park_start, park_end, time_duration_seconds)
    with open('output.txt', 'w') as output_file:
        # Iterate over the results and write the names to the output file
        for document in result:
            output_file.write(document.get('name', '') + '\n')

def pricing(result, time_duration, day_of_week, park_start, park_end, time_duration_seconds):
    result = result
    time_duration = time_duration

    day_of_week = day_of_week
    time_start = park_start.strftime("%H:%M")
    time_end = park_end.strftime("%H:%M")
    price_array = []

    time_seconds = time_duration_seconds
    # Calculate hours and minutes
    hours, remainder = divmod(time_seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    # Create a string representation
    time_duration_str = f"{int(hours)}:{int(minutes)}"

    for document in result:
        got_deal = False
        document_json = json.loads(json.dumps(document, default=str))

        # Declare main variables at the beginning
        # morning deal vars
        morning = document.get('prices', {}).get('specialPrice', {}).get('Morning', {})
        morning_prices = morning.get('price', {})
        morning_start = morning.get('start', [])
        morning_end = morning.get('end', [])

        # evening deal vars
        evening = document.get('prices', {}).get('specialPrice', {}).get('Evening', {})
        evening_prices = evening.get('price', {})
        evening_start = evening.get('start', [])
        evening_end = evening.get('end', [])

        # flat rate vars
        flat_rate = document.get('prices', {}).get('specialPrice', {}).get('flatRate', {})
        flat_rate_prices = flat_rate.get('prices', {})
        flat_rate_days = list(flat_rate_prices.keys())

        # regular parking vars
        reg_park = document.get('prices', {}).get('byDay')
        reg_park_prices = reg_park.get('all', {})

        print("CHECK-IN:",document.get('name', ''))

        # Check for morning deal
        if morning_prices and time_seconds < 86400 and not got_deal:
            print("MORNING:",document.get('name', ''))
            if len(morning_start) < 2:
                if time_start <= morning_start[0] and time_end >= morning_end[0]:
                    got_deal = True
                    price_array.append([document_json])
            else:
                print("MORNING:",document.get('name', ''))
                if time_start > morning_start[0] and time_start < morning_start[1] and time_end > morning_end[0]:
                    got_deal = True
                    price_array.append([document_json])

        # Check for evening deal
        if evening_prices and time_seconds < 86400 and not got_deal:
            print("EVENING:",document.get('name', ''))
            if time_start >= evening_start[0] and time_end <= evening_end[0]:
                got_deal = True
                price_array.append([document_json])

        # Check for flat rate
        if flat_rate_prices and not got_deal:
            print("FLAT:",document.get('name', ''))
            if day_of_week in flat_rate_days:
                got_deal = True
                price_array.append([document_json])

        # Regular parking prices
        if not got_deal:
            print("REG:",document.get('name', ''))
            for k,v in reg_park_prices.items():
                if time_duration_str <= k:
                    price_array.append([document_json])
                    break 
    print("PRICE LIST: ", price_array)

if __name__ == '__main__':
    app.run(debug=True)
