import stripe
from stripe import Charge
import time
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from ticket_selling_platform import settings
from itertools import chain
from tsp.models import Society, Order, EventCartItem, Payment
from tsp.views.helpers import StudentAccessMixin

stripe.api_key = settings.STRIPE_SECRET_KEY

@method_decorator(csrf_exempt, name='dispatch')
class PayoutView(StudentAccessMixin, View):
    """
    View that distributes payments to each society when an order is completed.
    """
    
    def post(self, request, order_id):
        """
        Distribute payment for a completed order to the respective sellers.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object.
        order_id : int
            The ID of the completed order.

        Returns
        -------
        HttpResponse
            A 204 No Content response.
        """
        
        # Retrieve the completed order and items associated with this order
        order = Order.objects.get(id=order_id)
        cart = order.student.cart
        order_items = self._get_order_items(cart)
        seller_items = self._get_order_items_by_seller(order_items)
        payouts = self._get_payouts(seller_items, cart)
        self._initiate_payout(order, payouts)
        return HttpResponse(status=204)
            
    def _get_order_items(self, cart):
        """
        Get the items associated with the given order.

        Parameters
        ----------
        cart : Cart
            The Cart object that is associated with the current order.

        Returns
        -------
        list
            A list of EventCartItem and Society objects associated 
            with the order.
        """
        
        event_cart_items = cart.event_cart_item.all()
        memberships = cart.membership.all()
        return list(chain(event_cart_items, memberships))
    
    def _get_order_items_by_seller(self, order_items):
        """
        Get the grouped order items by seller.

        Parameters
        ----------
        order_items : list of EventCartItem and Society objects
            The list of items associated with the completed order.

        Returns
        -------
        dict
            A dictionary where the keys are sellers (either event hosts or 
            membership societies) and the values are lists of items associated 
            with that seller.
        """
    
        seller_items = {}
        for item in order_items:
            if isinstance(item, EventCartItem):
                # For event cart items, the seller is the event host
                seller = item.event.host
            else:
                # For membership items, the seller is the membership society
                seller = item
            if seller not in seller_items:
                seller_items[seller] = []
            seller_items[seller].append(item)
        return seller_items
    
    def _get_payouts(self, seller_items, cart):
        """
        Get the payout amounts for each seller based on their items and any 
        discounts applied.

        Parameters
        ----------
        seller_items : dict
            A dictionary of seller items where the keys are sellers and the 
            values are lists of items associated.
        cart : Cart
            The Cart object that is associated with the current order.

        Returns
        -------
        dict
            A dictionary where the keys are sellers and the values are payout 
            amounts.
        """
    
        payouts = {}
        for seller, items in seller_items.items():
            payout_amount = 0
            for item in items:
                if isinstance(item, Society):
                    # Add the membership fee to the payout amount
                    payout_amount += item.member_fee
                else:
                    # Calculate the payout amount for the given event cart item
                    event = item.event
                    early_bird_total_price = item.early_bird_quantity * event.early_bird_price
                    standard_total_price = item.standard_quantity * event.standard_price
                    item_total_price = early_bird_total_price + standard_total_price
                    discount_data = cart.discount_data           
                    discount_applied = discount_data.get(item.id, 0)
                    item_total_price -= discount_applied   
                    if item_total_price > 0:
                        payout_amount += item_total_price       
            payouts[seller] = payout_amount
        return payouts
    
    def _initiate_payout(self, order, payouts):
        """
        Initiates payout to the sellers based on the given payout amounts.

        Parameters
        ----------
        order : Order
            The completed order object.
        payouts : dict
            A dictionary where the keys are the sellers and the values are the 
            payout amounts.
        """
    
        payment = Payment.objects.get(order=order)
        customer_id = order.customer_id
        customer = stripe.Customer.retrieve(order.customer_id) 
        payment_method_id = customer.invoice_settings.default_payment_method

        for seller, payout_amount in payouts.items():   
            payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
            intent = stripe.PaymentIntent.create(
                amount=int(payout_amount * 100),
                currency='gbp',
                payment_method=payment_method_id,
                customer=customer_id,
                payment_method_types=['card'],
                transfer_data={
                    'destination': seller.stripe_account_id
                },
            )
            intent.confirm()  
