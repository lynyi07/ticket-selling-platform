from django.core.management.base import BaseCommand
from tsp.models import University, Student, Society, StudentUnion, Domain, Event, Cart, EventCartItem, Order, Payment, Ticket, HistoricalCart

class Command(BaseCommand):
    """Command to unseed the database."""

    def handle(self, *args, **options):
        Ticket.objects.all().delete()
        Payment.objects.all().delete()
        EventCartItem.objects.all().delete()
        Cart.objects.all().delete()
        HistoricalCart.objects.all().delete()
        Order.objects.all().delete()
        Event.objects.all().delete()
        Student.objects.all().delete()
        Society.objects.all().delete()
        StudentUnion.objects.all().delete()
        University.objects.all().delete()
        Domain.objects.all().delete()