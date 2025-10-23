import stripe
import time
from django.views.generic.edit import UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from tsp.models import Society
from ticket_selling_platform import settings
from tsp.forms.society.bank_details_form import BankDetailsForm
from tsp.views.helpers import SocietyAccessMixin

stripe.api_key = settings.STRIPE_SECRET_KEY

class BankDetailsView(SocietyAccessMixin, UpdateView):
    """View that manages the bank details for a society account."""

    model = Society
    form_class = BankDetailsForm
    template_name = 'society/bank_details.html'
    
    def get_object(self, queryset=None):
        """Get the society object for the view."""
        
        self.society = self.request.user.society
        return self.society

    def form_valid(self, form):
        """
        Handle and validate the form submission.

        Parameters
        ----------
        form : ModifyBankDetailsForm
            The modify bank details form object.

        Returns
        -------
        HttpResponseRedirect
            A redirect response to the modify bank details page.
        """

        if not self.society.stripe_account_id:
            account = self._create_account(form)
            self._accept_terms(account)

        form.save()
        messages.success(self.request, "Bank details updated successfully!")
        return redirect(self.request.path_info)
    
    def _create_account(self, form):
        """
        Create the Stripe account for the current society.
        
        Parameters
        ----------
        form : BankDetailsForm
            The bank details form.

        Returns
        -------
        stripe.Account
            The Stripe account created.
        """

        account = stripe.Account.create(
            type='custom',
            country='GB',
            email=self.society.email,
            requested_capabilities=['card_payments', 'transfers'],
            business_type='individual',
            business_profile={
                # Merchant Category Code representing recreation services
                'mcc': '7999', 
                'url': 'https://www.kcl.ac.uk/',
            },
            individual={
                # General individual information is used to create Stripe account
                'dob': {
                    'day': 1,   
                    'month': 1,
                    'year': 2010,
                },
                'email': self.society.email,
                'first_name': self.society.name,
                'last_name': self.society.university.name,
                'phone': '+447388245863',
                'address': {
                    'line1': 'Bush House',
                    'city': 'London',
                    'postal_code': 'WC2R 2LS',
                    'country': 'GB'
                }
            },
            external_account={
                'object': 'bank_account',
                'country': 'GB',
                'currency': 'GBP',
                'routing_number': form.cleaned_data['sort_code'],
                'account_number': form.cleaned_data['account_number'],
                'account_holder_name': form.cleaned_data['account_name'],
            },
        )
        self.society.stripe_account_id = account.id
        self.society.save()
        return account
    
    def _accept_terms(self, account):
        """
        Accept the terms of service for the seller's account
        
        Parameters
        ----------
        account : stripe.Account
            The society's Stripe account.
        """
        
        account.tos_acceptance = {
            'date': int(time.time()),
            'ip': self.request.META.get('REMOTE_ADDR', None),
        }
        account.save()

    def form_invalid(self, form):
        """
        Handle invalid form submission.

        Parameters
        ----------
        form : ModifyBankDetailsForm
            The modify bank details form object.

        Returns
        -------
        HttpResponseRedirect
            A redirect response to the modify bank details page.
        """

        messages.error(self.request, "Failed to update bank details.")
        return super().form_invalid(form)