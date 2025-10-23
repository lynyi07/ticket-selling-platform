"""
Signal handlers for working with events and orders to promote loose coupling.

Functions
---------
cancel_event_when_host_deleted : function
    Cancel all events when the host society is deleted.
delete_event_cart_item_when_event_cancelled : function
    Delete EventCartItem objects when an event is cancelled.
delete_event_cart_item_when_removed_from_cart : function
    Delete EventCartItem objects when removed from the cart.
complete_order : function
    Handle order completion tasks such as creating historical carts,
    managing payment and ticket objects, and clearing the cart.
"""

from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.db import transaction
import json
from tsp.json_utils.json_encoder import DecimalEncoder
import stripe
from faker import Faker
import random
from tsp.views.student.payout_view import PayoutView
from django.test import RequestFactory
from tsp.models import (
    Society, 
    Event,
    HistoricalCart,
    EventCartItem, 
    Ticket, 
    Order,
    Payment
)

@receiver(pre_delete, sender=Society)
def cancel_event_when_host_deleted(sender, instance, **kwargs):
    """Cancel all events when the host society is deleted."""
    
    instance_events = Event.objects.filter(host=instance)
    for event in instance_events:
        event.cancel_event()
        event.host = None 
        event.save()
    
@receiver(post_save, sender=EventCartItem)
def delete_event_cart_item_when_event_cancelled(sender, instance, **kwargs):
    """
    Deletes all EventCartItem objects associated with an event when the event
    status is changed to 'CANCELLED'.
    """
    
    if instance.event.status == 'CANCELLED':
        instance.delete()

@receiver(pre_save, sender=EventCartItem)
def delete_event_cart_item_when_removed_from_cart(sender, instance, **kwargs):
    """
    Deletes all EventCartItem objects associated with an event when the event
    status is changed to 'CANCELLED' or both the standard quantity and early
    bird quantity are 0.
    """
    
    if instance.id and instance.standard_quantity == 0 and instance.early_bird_quantity == 0:
        instance.delete()

@receiver(post_save, sender=Order)
def complete_order(sender, instance, created, **kwargs):
    """ 
    After a new order is placed, create a historical cart with data from 
    user's cart, create the payment and ticket objects, issue tickets, 
    then empty the cart.
    """ 

    if created:
        with transaction.atomic():
            cart = instance.student.cart
            _create_historical_cart(cart, instance)
            _create_payment(cart, instance)
            _create_ticket(cart, instance)
            if instance.customer_id and not instance.customer_id.startswith('fake'): 
                _distribute_payment(instance)
            _update_order_items(cart, instance)
            _clear_cart(cart)
            
def _create_historical_cart(cart, order):
    """
    Create a new historical cart with data from user's cart.
    
    Parameters:
    -----------
    cart : Cart
        The user's cart object.
    order : Order
        The order object that was just created.
    """
    
    historical_cart = HistoricalCart.objects.create(
        student=order.student,
        order=order,
        total_price=cart.total_price,
        total_saved=cart.total_saved,
        count=cart.count,
        discount_data=json.dumps(cart.discount_data, cls=DecimalEncoder)
    )
    
    # Set event and membership cart items with data from cart
    for item in cart.event_cart_item.all():
        historical_cart.event_cart_item.add(item)
    for item in cart.membership.all():
        historical_cart.membership.add(item)
    historical_cart.save()

def _update_order_items(cart, order):
    """
    Update the status of items after order has been placed.
    
    Parameters:
    -----------
    cart : Cart
        The user's cart object.
    order : Order
        The order object that was just created.
    """
    
    for item in cart.event_cart_item.all():
        _update_cart_item_after_order_completed(item, cart, order.student)
    for item in cart.membership.all():
        _update_cart_item_after_order_completed(item, cart, order.student)

def _update_cart_item_after_order_completed(item, cart, student):
    """
    Update items in the cart after an order has been completed.
    If the item is an event cart item, set it as purchased.
    If the item is a membership, set the current student as a regular member.
    
    Parameters:
    -----------
    cart : Cart
        The user's cart object.
    student : Student 
        The student who placed the order.
    """
    
    discount_data = cart.discount_data
    if isinstance(item, EventCartItem):
        student.purchase_event(item.event)
        if item.id in discount_data:
            student.purchase_discounted_event(item.event)
    elif isinstance(item, Society):
        item.add_regular_member(student)
    item.save()

def _clear_cart(cart):
    """
    Clear the given cart by removing all the items and save the changes.
    
    Parameters:
    -----------
    cart : Cart
        The user's cart object.
    """
    
    cart.clear()
    cart.save()
    
def _create_payment(cart, order):
    """
    Create a new payment object with data from the completed order 
    when the order is not free.
    
    Parameters:
    -----------
    cart : Cart
        The user's cart object.
    order : Order
        The order object that was just created.
    """
    
    if order.customer_id:
        try:
            customer = stripe.Customer.retrieve(order.customer_id)
            payment_method_id = customer.invoice_settings.default_payment_method
            payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
            last4 = payment_method.card.last4
            brand = payment_method.card.brand
            transaction_id = payment_method_id
        except:
            # For seeding purposes
            transaction_id = "pm_" + Faker("en_GB").sha1()
            last4 = random.randint(1000,9999)
            brands = ["visa", "mastercard", "amex", "unionpay"]
            brand = random.sample(brands, k=1)[0]
        Payment.objects.create(
            student=order.student,
            order=order,
            amount=cart.total_price,
            last4=last4,
            brand=brand,
            transaction_id=transaction_id
        )
    
def _create_ticket(cart, order):
    """
    Create tickets for the event cart items in the given cart.

    Parameters:
    -----------
    cart : Cart
        The cart object containing the event cart items.
    order : Order
        The order object to which the tickets belong.
    """
    
    for item in cart.event_cart_item.all():
        _create_ticket_for_quantity(
            item, 
            order, 
            item.early_bird_quantity, 
            'early_bird'
        )
        _create_ticket_for_quantity(
            item, 
            order, 
            item.standard_quantity, 
            'standard'
        )

def _create_ticket_for_quantity(item, order, quantity, ticket_type):
    """
    Create tickets for the given item, order and ticket type, for a given 
    quantity.

    Parameters:
    -----------
    item : Item
        The event cart item.
    order : Order
        The order object to which the tickets belong.
    quantity : int
        The quantity of tickets to be created.
    ticket_type : str
        The type of ticket to be created, either EarlyBird or Standard.
    """
    
    for i in range(quantity):
        ticket = Ticket.objects.create(
            event=item.event,
            order=order,
            type=ticket_type,
        )
        ticket.save()
        
def _distribute_payment(order):
    """
    Distribute the payment for a completed order to the sellers.

    Parameters:
    -----------
    order : Order 
        The completed order to distribute the payment for.
    """

    # Create a fake request object  
    factory = RequestFactory()
    request = factory.post('/')
    
    # Call the post method on the payout view with the fake request
    payout_view = PayoutView()
    payout_view.post(request, order.id)