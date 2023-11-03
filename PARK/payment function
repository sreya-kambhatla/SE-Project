import stripe
from flask import Flask, jsonify, request

# Stripe secret key
stripe.api_key = 'your_secret_key'

@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        # Calculate the order total on the server to prevent
        # people from manipulating the amount on the client
        amount = calculate_order_amount(request.json['items'])

        # Create a payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            # Verify your integration in this guide by including this parameter
            metadata={'integration_check': 'accept_a_payment'},
        )

        return jsonify({
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        return jsonify(error=str(e)), 403
