/**
 * This file contains JavaScript code for handling the Stripe payment process, 
 * including creating a card element, validating user input in real-time, 
 * and sending the payment method to the server.
 */

const stripe = Stripe(window.STRIPE_PUBLIC_KEY);
const elements = stripe.elements();
const card = elements.create('card');
card.mount('#card-element');

// Handle real-time validation errors from the card Element
card.addEventListener('change', function(event) {
  var displayError = document.getElementById('card-errors');
  if (event.error) {
    displayError.textContent = event.error.message;
  } else {
    displayError.textContent = '';
  }
});

const form = document.getElementById('payment-form');

form.addEventListener('submit', function(event) {
  event.preventDefault();

  // Disable the submit button to prevent multiple clicks
  document.getElementById('submit-button').disabled = true;

  // Create a payment method using the card Element 
  stripe.createPaymentMethod('card', card).then(function(result) {
    if (result.error) {
      // Inform the user if there was an error and re-enable the submit button
      var errorElement = document.getElementById('card-errors');
      errorElement.textContent = result.error.message;
      document.getElementById('submit-button').disabled = false;
    } else {
      // Send the payment method to the server
      stripePaymentMethodHandler(result.paymentMethod);
    }
  });
});

// Send the payment method to the server
function stripePaymentMethodHandler(paymentMethod) {
  // Insert the PaymentMethod ID into the form and submit it to the server.
  var hiddenInput = document.createElement('input');
  hiddenInput.setAttribute('type', 'hidden');
  hiddenInput.setAttribute('name', 'payment_method_id');
  hiddenInput.setAttribute('value', paymentMethod.id);
  form.appendChild(hiddenInput);
  form.submit();
}
