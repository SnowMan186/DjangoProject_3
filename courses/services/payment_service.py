import stripe
import os
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product_and_price(course):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    """
    Создает Продукт и Цену в Stripe.
    """
    try:
        # 1. Создаем Продукт (Product)
        product = stripe.Product.create(
            name=course.title,
            description=course.description,
        )

        # 2. Создаем Цену (Price).
        # В Stripe цены хранятся в минимальных единицах валюты (копейки).
        # Если цена курса 5000 руб., то для Stripe это 500000.
        price_amount = int(course.price * 100)

        price = stripe.Price.create(
            unit_amount=price_amount,
            currency="rub",
            product=product.id,
        )
        return product, price

    except stripe.error.StripeError as e:
        # Обработка ошибок Stripe (например, неверный формат данных)
        print(f"Stripe Error: {e}")
        return None, None


def create_checkout_session(price_id):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    """
    Создает Сессию оплаты (Checkout Session) по ID цены.
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://127.0.0.1:8000/success/',
            cancel_url='http://127.0.0.1:8000/cancel/',
        )
        return session
    except stripe.error.StripeError as e:
        print(f"Stripe Session Error: {e}")
        return None