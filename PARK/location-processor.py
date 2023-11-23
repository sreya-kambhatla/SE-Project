'''
This flask app initializes homepage.html as the default page.
Location.processor.py then receives the location entered on the 
homepage, redirects to /search (not a real page) which sends
that location value to results.html to be used in results.js
'''

from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)

# root page is homepage.html
@app.route('/')
def index():
    return render_template('homepage.html')
'''
location value is gathered from the get method
in homepage.html and then the page is redirected to search
(which isn't a real page)
'''
@app.route('/search', methods=['GET'])
def search():
    location = request.args.get('location')
    
    # Check if a location is provided
    if location:
        # If location is provided, redirect to /results with the provided location
        redirect_url = url_for('results', location=location, userEntered=True)
    else:
        # If location is not provided, set a default location and redirect to /results
        default_location = 'New York, NY'
        redirect_url = url_for('results', location=default_location, userEntered=False)

    return redirect(redirect_url)

@app.route('/results')
def results():
    flaskLocation = request.args.get('location', '')
    userEntered = request.args.get('userEntered', False)
    print(flaskLocation, userEntered)
    return render_template('results.html', flaskLocation=flaskLocation, userEntered=userEntered)

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


# IMPORTANT: when webpage is ready, remove the code below
if __name__ == '__main__':
    app.run(debug=True)