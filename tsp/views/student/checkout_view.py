from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView
from tsp.views.helpers import StudentAccessMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from tsp.models import Order, Payment, Ticket, HistoricalCart
import stripe
import os
from tsp.forms.student.checkout_form import CheckoutForm
from django.core.mail import send_mail
from ticket_selling_platform import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

@method_decorator(csrf_exempt, name='dispatch')
class CheckoutView(StudentAccessMixin, FormView):
    """
    View for handling the checkout process, including creating a new 
    order, processing payment with Stripe, clearing the shopping 
    cart and updating inventory.
    """
    
    template_name = 'student/checkout.html'
    form_class = CheckoutForm
    
    def dispatch(self, request, *args, **kwargs):
        """
        Set the student and cart objects and dispatch the request 
        to the superclass.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object.

        Returns
        -------
        HttpResponse
            The HTTP response object returned by the superclass.
        """
        
        if hasattr(request.user, 'student'):
            self.student = request.user.student
            self.cart = self.student.cart

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Get the context data to be used in rendering the template.

        Returns
        -------
        dict
            A dictionary containing the following key(s):
            - 'STRIPE_PUBLIC_KEY': The public STRIPE API key.
            - 'email': The student's email.
        """
        
        context = super().get_context_data(**kwargs)
        context.update({
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
            'email': self.student.email,
        })
        return context
    
    def get_form(self, form_class=None):
        """
        Get an instance of the form to be used in this view.

        Returns
        -------
        form
            An instance of the form to be used in this view.
        """
        
        form = super().get_form(form_class)
        form.initial['amount'] = self.cart.total_price
        form.initial['email'] = self.student.email
        return form
    
    def get(self, request, *args, **kwargs):
        """
        Handle the GET request to the checkout view.

        If all items in the cart are free, create a new order and redirect
        to the order detail page. Otherwise, return the checkout page view.

        Parameters
        ----------
        request : HttpRequest
            The request object used to generate the view.

        Returns
        -------
        HttpResponse
            The HTTP response object that represents the view.
        """

        if self.cart.all_items_free:
            order = self._create_order(None)
            self._send_order_confirmation(order, None)
            return redirect('order_detail', pk=order.pk)
        return super().get(request, *args, **kwargs)

    @transaction.atomic
    def form_valid(self, form):    
        """
        Handle valid form submissions.
        
        Parameters
        ----------
        form : CheckoutForm
            The form instance containing the valid data.
        
        Returns
        -------
        HttpResponseRedirect
            Redirect the user to the success URL upon successful form 
            submission.
        """
        
        # Convert GBP to pence
        amount = int(form.initial['amount'] * 100)
        payment_method_id = form.cleaned_data['payment_method_id']
        try:
            # Create a customer object
            customer = stripe.Customer.create(
                name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
            )
         
            # Attach the payment method to the customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer.id,
            )

            # Set the payment method as default payment method for the customer
            stripe.Customer.modify(
                customer.id,
                invoice_settings={
                    'default_payment_method': payment_method_id,
                },
            )
        
            # Create a new order
            order = self._create_order(form, customer.id)
    
        except stripe.error.StripeError as e:
            self._handle_stripe_error(e)
            return self.form_invalid(form) 

        except Exception as e:
            self._handle_generic_error()
            return self.form_invalid(form)
             
        self._send_order_confirmation(order, form)
        return redirect('order_detail', pk=order.pk)
            
    def _create_order(self, form, customer_id=None):
        """
        Create a new order with the submitted form data.
        
        Parameters
        ----------
        form : CheckoutForm
            The form instance containing the submitted data.
        charge_id : str
            The charge ID for the Stripe payment if applicable.
         
        Returns
        -------
        Order
            The newly created order instance.
        """
        
        if form is not None:
            line_1 = form.cleaned_data.get('line_1')
            line_2 = form.cleaned_data.get('line_2', '')
            city_town = form.cleaned_data.get('city_town')
            postcode = form.cleaned_data.get('postcode')
            country = form.cleaned_data.get('country')
        else:
            line_1, line_2, city_town, postcode, country = '', '', '', '', ''
            
        order = Order.objects.create(
            student=self.student,
            line_1=line_1,
            line_2=line_2,
            city_town=city_town,
            postcode=postcode,
            country=country,
            customer_id=customer_id,
        )
        return order
        
    def _handle_stripe_error(self, e):
        """
        Handle Stripe errors.

        Parameters
        ----------
        e : StripeError
            The Stripe error object.
        """
        
        if isinstance(e, stripe.error.CardError):
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"Card Error: {err.get('message')}")
        elif isinstance(e, stripe.error.RateLimitError):
            messages.error(
                self.request, 
                'Rate Limit Error: Too many requests made. Try again later.'
            )
        elif isinstance(e, stripe.error.InvalidRequestError):
            messages.error(
                self.request, 
                'The minimum checkout amount is GBP£0.3.'
            )
        elif isinstance(e, stripe.error.APIConnectionError):
            messages.error(
                self.request, 
                'API Connection Error: Check your network connection.'
            )
        elif isinstance(e, stripe.error.AuthenticationError):
            messages.error(
                self.request, 
                'Authentication with Stripe API failed. Please contact support.'
            )
        else:
            messages.error(
                self.request, 
                'Something went wrong. You were not charged. Please try again.'
            )
    
    def _handle_generic_error(self):
        """Handle generic errors."""

        messages.error(
            self.request, 
            'Generic error: Something went wrong. You were not charged. Please try again.'
        )
        
    def form_invalid(self, form):
        """
        Handle invalid form submissions.

        Parameters
        ----------
        form : CheckoutForm
            The form instance containing the invalid data.

        Returns
        -------
        HttpResponse
            Render the checkout form.
        """
        
        return super().form_invalid(form)
    
    def _send_order_confirmation(self, order, form):
        """
        Send an email confirmation for the given order.

        Parameters
        ----------
        order : Order
            The order for which to send the receipt.
        form : CheckoutForm
            The form containing checkout information.
        """
        
        subject = f"We have received your order #{order.id}"
        from_email = settings.EMAIL_HOST_USER
        
        if form:
            to_email = form.cleaned_data['email']
        else:
            to_email = self.student.email
        
        try:
            payment = Payment.objects.get(order=order)
        except Payment.DoesNotExist:
            payment = None
    
        context = ({
            'order': order,
            'tickets': Ticket.objects.filter(order=order),
            'payment': payment,
            'cart': HistoricalCart.objects.get(order=order)
        })
        html_message = render_to_string(
            'student/email/order_confirmation.html', 
            context
        )

        # Create the email and attach the HTML message.  
        msg = EmailMultiAlternatives(
            subject,
            '',
            from_email,
            [to_email],
        )
        msg.attach_alternative(html_message, "text/html")

        # send the email
        msg.send()

