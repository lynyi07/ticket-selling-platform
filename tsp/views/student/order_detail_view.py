from django.views.generic import DetailView
from tsp.views.helpers import StudentAccessMixin
from django.shortcuts import get_object_or_404
from tsp.models import Order, HistoricalCart, Payment

class OrderDetailView(StudentAccessMixin, DetailView):
    """View for a student to view an order."""
    
    model = Order
    template_name = 'student/order_detail.html'
    context_object_name = 'order'
    
    def get_context_data(self, **kwargs):
        """
        Get context data for the order detail view.
        
        Returns
        -------
        dict
            A dictionary containing the following key(s):
            - 'total_price': The total price of the order.
            - 'total_saved': The total saved from the order.
            - 'event_cart_items': The events in the order.
            - 'memberships': The memberships in the order.
            - 'payment': The payment object.
        """
        
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        historical_cart = HistoricalCart.objects.get(order=order)

        try:
            payment = Payment.objects.get(order=order)
        except Payment.DoesNotExist:
            # When order amount is 0
            payment = None 
        
        context.update({
            'total_price': historical_cart.total_price,
            'total_saved': historical_cart.total_saved,
            'discount_data': historical_cart.discount_data_dict,
            'event_cart_items': historical_cart.event_cart_item.all(),
            'memberships': historical_cart.membership.all(),
            'payment' : payment,
        })
        return context

    def get_object(self):   
        """
        Get the order object with the given primary key for the currently 
        authenticated student.
        
        Returns
        -------
        Order
            The requested order object if it belongs to the student.
        Http404
            If the order does not belong to the student.
        """
        
        return get_object_or_404(   
            Order, 
            pk=self.kwargs.get('pk'), 
            student=self.request.user.student
        )