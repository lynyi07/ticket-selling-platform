from django.views.generic import DetailView
from tsp.models import Cart 
from tsp.views.helpers import StudentAccessMixin
from tsp.forms.student.update_cart_form import UpdateCartForm

class CartDetailView(StudentAccessMixin, DetailView):
    """View that displays a details of a cart.""" 

    model = Cart
    template_name = 'student/cart_detail.html'
    form_class = UpdateCartForm
    
    def get_object(self, queryset=None):
        """Return the cart instance associated with the current user."""
        
        cart,_ = Cart.objects.get_or_create(student=self.request.user.student)
        return cart
    
    def get_context_data(self, **kwargs):
        """
        Get the template context for rendering the cart detail page.
        
        Returns
        -------
        dict
            A dictionary containing the following key(s):
            - 'event_cart_items': A queryset of all the event cart items in the cart.
            - 'memberships': A list of all society memberships in the given cart.
            - 'total_saved': The total amount saved through discounts.
            - 'total_price': The total price of all items in the cart with discounts applied.
            - 'count': The total number of items in the cart.
        """ 
        
        context = super().get_context_data(**kwargs)
        cart = self.object
        memberships = cart.membership.all()
        event_cart_items = cart.event_cart_item.all()
        total_saved =cart.total_saved
        total_price = cart.total_price
        count = cart.count
 
        context.update({
            'event_cart_items': event_cart_items,
            'memberships': memberships,
            'total_saved': total_saved,
            'total_price': total_price,
            'count': count,
        })

        return context