from django.views.generic import View
from django.urls import reverse_lazy 
from tsp.models import Cart, EventCartItem, Society
from django.shortcuts import get_object_or_404, redirect
from tsp.forms.student.update_cart_form import UpdateCartForm
from tsp.views.helpers import StudentAccessMixin
from django.http import JsonResponse
from django.views.generic.edit import FormMixin

class UpdateCartView(StudentAccessMixin, FormMixin, View):
    """View that updates cart items."""
    
    template_name = 'student/cart_detail.html'
    form_class = UpdateCartForm
    model = Cart
    success_url = reverse_lazy('cart_detail')

    def get_object(self, queryset=None):
        """
        Returns the Cart object for the current user.

        Parameters
        ----------
        queryset : QuerySet, optional
            The queryset to use for the search.

        Returns
        -------
        Cart
            The Cart object for the current user.
        """
        
        cart = Cart.objects.get(student=self.request.user)
        return cart
    
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to the view.

        Parameters
        ----------
        request : HttpRequest
            The request object.

        Returns
        -------
        HttpResponse or JsonResponse
            The HTTP response or JSON response.
        """
        
        cart = self.get_object()
        event_cart_item_id = request.GET.get('event_cart_item_id')
        if event_cart_item_id:
            event_cart_item = get_object_or_404(EventCartItem, pk=event_cart_item_id)
            form = self.form_class(event=event_cart_item.event) 
            form.cart=cart

        # Return a JSON response with the available ticket quantities when 
        # the request is an AJAX request and the action is to get the maximum 
        # ticket availability
        if (request.headers.get('x-requested-with') == 'XMLHttpRequest' 
            and request.GET.get('action') == 'get_max_availability'):
            early_bird_availability = form._get_available_ticket_quantities('early_bird')
            standard_availability = form._get_available_ticket_quantities('standard')
            return JsonResponse({
                'early_bird_availability': early_bird_availability,
                'standard_availability': standard_availability,
            })

        return redirect('cart_detail')
    
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to the view.

        Parameters
        ----------
        request : HttpRequest
            The request object.

        Returns
        -------
        JsonResponse
            The JSON response.
        """
        
        cart = self.get_object()
        event_cart_item = self._get_event_cart_item(cart, request)
        membership_to_remove = self._get_membership_to_remove(request)
        form = self._handle_form_data(request, membership_to_remove, cart)
        form.event_cart_item=event_cart_item
        if form.is_valid():         
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
        
    def _get_event_cart_item(self, cart, request):
        """
        Get the corresponding EventCartItem object based on the provided 
        EventCartItem ID.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object.

        Returns
        -------
        Society or None
            The EventCartItem object corresponding to the provided EventCartItem 
            ID, or None if the ID is not provided or does not correspond to a 
            valid EventCartItem object.
        """
        
        event_cart_item_id = request.POST.get('event_cart_item_id') 
        try:
            event_cart_item = EventCartItem.objects.get(id=event_cart_item_id)
        except EventCartItem.DoesNotExist:
            event_cart_item = None
        return event_cart_item
    
    def _get_membership_to_remove(self, request):
        """
        Get the corresponding Membership object based on the provided 
        membership ID.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object.

        Returns
        -------
        Society or None
            The Society object corresponding to the provided membership ID,
            or None if the ID is not provided or does not correspond to a 
            valid Society object.
        """
        
        membership_to_remove_id = request.POST.get('membership_to_remove_id')
        try:
            membership_to_remove = Society.objects.get(id=membership_to_remove_id)
        except Society.DoesNotExist:
            membership_to_remove = None
        return membership_to_remove
    
    def _handle_form_data(self, request, membership_to_remove, cart):
        """
        Handle the form data by setting copied data and initializing the form.

        Parameters
        ----------
        request : HttpRequest
            The request object.
        membership_to_remove : Society
            The Society object to remove from the cart.
        cart : Cart
            The current student's cart.

        Returns
        -------
        UpdateCartForm
            The initialized UpdateCartForm instance.
        """
        
        # Set the copied data 
        data=request.POST.copy() 
        data['membership'] = membership_to_remove
        
        # Initialse the form  
        form = self.form_class(
            data=data,
            user=request.user, 
            instance=cart,
            membership=membership_to_remove, 
        )
        return form
