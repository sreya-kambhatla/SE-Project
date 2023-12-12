@app.route('/success')
def success():
    session_id = request.args.get('session_id')
    if session_id:
        # Perform operations post successful payment (e.g., update order status, send confirmation email)
        return render_template('success.html')  # A template to show on successful payment
    else:
        return redirect(url_for('index'))  # Redirect to home or another appropriate page
