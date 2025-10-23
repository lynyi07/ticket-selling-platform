from django.shortcuts import get_object_or_404
from django.views.generic.edit import View
from django.contrib import messages
from django.shortcuts import render, redirect 
from tsp.models import Event 
from tsp.forms.student.add_to_cart_form import AddToCartForm
from tsp.views.helpers import StudentAccessMixin

class AddToCartView(StudentAccessMixin, View):
    """View that allows students to add an item to the cart."""
    
    template_name = 'student/event_page.html'
    success_message = 'Added to basket.'
    error_message = 'Something went wrong...'

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to the add to cart view.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object.

        Returns
        -------
        HttpResponseRedirect
            Redirect to the event detail page if the item is successfully added
            to the cart. Otherwise, render the form with error messages.

        Notes
        -----
        Get or create the cart for the current user. 
        If the form is valid, create and add the cart item into the user's cart. 
        Otherwise generate an error message and return user to the event details 
        page.
        """
        
        event = get_object_or_404(Event, pk=request.POST['event_pk'])
        form = AddToCartForm(request.POST, user=request.user, event=event)
        if form.is_valid():
            self.cart = form.save()
            if (form.cleaned_data['early_bird_to_add'] or 
                form.cleaned_data['standard_to_add'] or 
                form.cleaned_data['membership']):
                messages.success(request, self.success_message)
            return redirect('event_page', pk=event.id)
        else:
            messages.error(request, self.error_message)
            context = {'event': event, 'form': form}
            return render(request, self.template_name, context=context)