@app.route('/cancel')
def cancel():
    # Logic to handle cancellation
    return render_template('cancel.html')  # A template to show when payment is canceled
