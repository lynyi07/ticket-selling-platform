from django.shortcuts import get_object_or_404
from django.views.generic.edit import View
from django.shortcuts import redirect 
from tsp.models import Society, Cart
from tsp.views.helpers import StudentAccessMixin

class BuyMembershipView(StudentAccessMixin, View):
    """
    View that allows students to add a society membership to the cart on 
    the society page.
    """

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to the buy membership view.

        Parameters
        ----------
        request : HttpRequest
            The request object for the HTTP request.

        Returns
        -------
        HttpResponseRedirect
            A redirect response to the cart detail page.
        """
        
        student = request.user.student
        cart = get_object_or_404(Cart, student=student)
        society_pk = request.POST['society_pk']
        membership = get_object_or_404(Society, pk=society_pk)
        cart.membership.add(membership)
        cart.save()
        return redirect('cart_detail')
