/**
 * This file contains JavaScript code for updating the shopping cart on the 
 * events page. It includes functionality for incrementing and decrementing 
 * the quantity of tickets in the cart, as well as removing memberships from 
 * the cart. It also includes a function for retrieving the maximum 
 * availability of a given ticket type for an event cart item.
 */

// Get the update cart form and update cart URL from the page
const updateCartForm = document.querySelector('#update-cart-form');
const updateCartUrl = window.updateCartUrl;

// Get the availability spans for each ticket type
const earlyBirdSpan = document.getElementById('early_bird_availability');
const standardSpan = document.getElementById('standard_availability');

// Get all the increment and decrement buttons on the page
const incrementButtons = document.querySelectorAll('.quantity-increment');
const decrementButtons = document.querySelectorAll('.quantity-decrement');

// Loop through all increment buttons and add a click event listener
incrementButtons.forEach(button => {
  button.addEventListener('click', async (event) => {
    event.preventDefault();

    // Get the event cart item ID and the input element containing the quantity value
    const eventCartItemId = event.target.getAttribute('data-event-cart-item-id');
    const inputEl = event.target.parentElement.querySelector('input');
    let currentValue = parseInt(inputEl.value) || 0;

    // Get the ticket type and maximum availability for the event cart item
    const ticketType = inputEl.getAttribute('data-ticket-type');
    const maxAvailability = await getMaxAvailability(eventCartItemId, ticketType);

    // Increment the input value if maximum availability has not been reached
    if (maxAvailability <= 0) {
      return;
    }
    inputEl.value = currentValue + 1;
    
    // Create a new form data object and append the necessary data
    const data = new FormData(updateCartForm);
    data.append('event_cart_item_id', eventCartItemId);
    if (ticketType === 'standard') {
      data.append('standard_to_add', 1);
    } else if (ticketType === 'early_bird') {
      data.append('early_bird_to_add', 1);
    }

    // Send the update request. Update the availability spans and reload the 
    // page if successful
    const response = await fetch(updateCartUrl, {
      method: 'POST',
      body: data
    });
    if (response.ok) {
      const jsonResponse = await response.json();
      if (jsonResponse.early_bird_availability) {
        earlyBirdSpan.innerText = jsonResponse.early_bird_availability;
      }
      if (jsonResponse.standard_availability) {
        standardSpan.innerText = jsonResponse.standard_availability;
      }
      location.reload();
    }
  });
});

// Add an event listener for each decrement button
decrementButtons.forEach(button => {
  button.addEventListener('click', async (event) => {
    event.preventDefault();

    // Get the event cart item ID and current input value
    const eventCartItemId = event.target.getAttribute('data-event-cart-item-id');
    const inputEl = event.target.parentElement.querySelector('input');
    let currentValue = parseInt(inputEl.value) || 0;

    // Decrement the input value if minimum allowed has not been reached
    if (currentValue - 1 < parseInt(inputEl.getAttribute('min'))) {
      return;
    }
    inputEl.value = currentValue - 1;
    
    // Create a new form data object and append the necessary data
    const data = new FormData(updateCartForm);
    data.append('event_cart_item_id', eventCartItemId);

    // Determine the ticket type and adjust the quantity accordingly
    const ticketType = inputEl.getAttribute('data-ticket-type');
    if (ticketType === 'standard') {
      data.append('standard_to_add', -1);
    } else if (ticketType === 'early_bird') {
      data.append('early_bird_to_add', -1);
    }
    
    // Send the update request. Update the availability spans and reload the 
    // page if successful
    const response = await fetch(updateCartUrl, {
      method: 'POST',
      body: data
    });
    if (response.ok) {
      const jsonResponse = await response.json();
      if (jsonResponse.early_bird_availability) {
        earlyBirdSpan.innerText = jsonResponse.early_bird_availability;
      }
      if (jsonResponse.standard_availability) {
        standardSpan.innerText = jsonResponse.standard_availability;
      }
      location.reload();
    }
  });
});

// Get all remove membership buttons and attach event listener to each
const removeMembershipButtons = document.querySelectorAll('.remove-membership');
removeMembershipButtons.forEach(button => {
  button.addEventListener('click', async (event) => {
    event.preventDefault();
    // Get the ID of the membership to be removed
    const cartItemId = event.target.getAttribute('data-membership-id');

    // Create a new FormData object and append the membership ID to it
    const data = new FormData(updateCartForm);
    data.append('membership_to_remove_id', cartItemId);

    // Send a POST request to update the cart with the removed membership.
    // Reload the page to update the cart if successful.
    const response = await fetch(updateCartUrl, {
      method: 'POST',
      body: data
    });
    if (response.ok) {
      location.reload();
    } else {
      const error = await response.json();
      console.error(`Error: ${error.detail}`);
    }
  });
});

/**
  * A function that retrieves the maximum availability of a given ticket  
  * type for an event cart item.
  * @param {string} eventCartItemId - The ID of the event cart item.
  * @param {string} ticketType - The type of ticket to retrieve availability 
  * for (e.g. 'early_bird' or 'standard').
  */
async function getMaxAvailability(eventCartItemId, ticketType) {
  try {
    // Send a GET request to the server to retrieve the maximum availability 
    // of the ticket type for the event cart item.
    const response = await fetch(
      `${updateCartUrl}?action=get_max_availability&event_cart_item_id=${eventCartItemId}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        }
      }
    );    
    
    // Parse the response JSON and return the maximum availability of the 
    // specified ticket type.
    const jsonResponse = await response.json();
    return jsonResponse[`${ticketType}_availability`];
  } catch (err) {
    console.error(err);
  }
}