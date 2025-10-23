from tsp.views.helpers import StudentAccessMixin
from django.views.generic import ListView
from tsp.models import Order

class ListOrderHistoryView(StudentAccessMixin, ListView):
    """View that displays a list of orders for a student account."""   

    model = Order 
    template_name = 'student/order_history_list.html'
    context_object_name = "order"

    def get_queryset(self):
        """
        Return a queryset of orders associated with the current logged-in 
        student user.

        Returns
        -------
        QuerySet
            A queryset of Order objects associated with the current logged-in 
            student user.
        """
        
        user = self.request.user
        return Order.get_orders_by_student(user)