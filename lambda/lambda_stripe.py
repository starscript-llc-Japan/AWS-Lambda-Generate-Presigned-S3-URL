import json
import stripe
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

stripe.api_key = ""

def lambda_handler(event, context):
    try:
        logger.info("Event: %s", event)  # Check what kind of request this is

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'AI Tool Download'},
                    'unit_amount': 300,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://',
            cancel_url='https://'
        )

        logger.info("Stripe session created: %s", session.id)

        return {
            "statusCode": 302,
            "headers": {"Location": session.url}
        }

    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
