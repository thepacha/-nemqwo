import stripe
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from decouple import config
from models import User, Subscription
from datetime import datetime, timedelta

stripe.api_key = config("STRIPE_SECRET_KEY", default="")

class PaymentService:
    def __init__(self):
        self.stripe_secret_key = config("STRIPE_SECRET_KEY", default="")
        self.stripe_publishable_key = config("STRIPE_PUBLISHABLE_KEY", default="")
        
    async def create_customer(self, user: User) -> str:
        """Create a Stripe customer for the user"""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={"user_id": str(user.id)}
            )
            return customer.id
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create customer: {str(e)}"
            )
    
    async def create_subscription(self, customer_id: str, price_id: str) -> dict:
        """Create a subscription for the customer"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
            )
            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status
            }
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create subscription: {str(e)}"
            )
    
    async def cancel_subscription(self, subscription_id: str) -> dict:
        """Cancel a subscription"""
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            return {"status": subscription.status}
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to cancel subscription: {str(e)}"
            )
    
    async def get_subscription_status(self, subscription_id: str) -> dict:
        """Get subscription status from Stripe"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get subscription: {str(e)}"
            )
    
    async def create_checkout_session(self, customer_id: str, price_id: str, success_url: str, cancel_url: str) -> str:
        """Create a Stripe Checkout session"""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return session.url
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create checkout session: {str(e)}"
            )
    
    async def handle_webhook(self, payload: str, sig_header: str) -> dict:
        """Handle Stripe webhook events"""
        webhook_secret = config("STRIPE_WEBHOOK_SECRET", default="")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Handle the event
        if event["type"] == "customer.subscription.created":
            subscription = event["data"]["object"]
            return {"type": "subscription_created", "subscription": subscription}
        elif event["type"] == "customer.subscription.updated":
            subscription = event["data"]["object"]
            return {"type": "subscription_updated", "subscription": subscription}
        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            return {"type": "subscription_deleted", "subscription": subscription}
        elif event["type"] == "invoice.payment_succeeded":
            invoice = event["data"]["object"]
            return {"type": "payment_succeeded", "invoice": invoice}
        elif event["type"] == "invoice.payment_failed":
            invoice = event["data"]["object"]
            return {"type": "payment_failed", "invoice": invoice}
        
        return {"type": "unhandled", "event_type": event["type"]}

payment_service = PaymentService()