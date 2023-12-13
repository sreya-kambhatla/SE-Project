pip install stripe
import stripe
from flask import request, jsonify

# Set your secret key: remember to change this to your live secret key in production
stripe.api_key = "sk_test_yourSecretKey"

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Parking Reservation Fee',
                    },
                    'unit_amount': 2000,  # $20.00 in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.host_url + 'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'cancel',
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403
