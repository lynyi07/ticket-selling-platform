"""Unit tests of the Ticket model"""
from django.test import TestCase
from decimal import Decimal
from tsp.models import Payment, Order, Student, HistoricalCart, Ticket, Event

class PaymentModelTestCase(TestCase):
    """Unit tests of the Ticket model"""
    
    fixtures = [
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/default_event.json',
        'tsp/tests/fixtures/default_cart.json',
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_order.json'
    ]

    def setUp(self):
        self.student = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.order = Order.objects.get(pk=29)
        self.payment = Payment.objects.get(order=self.order)
        self.event = Event.objects.get(name='Default test event')
    
    def test_type_choices(self):
        choices = Ticket._meta.get_field("type").choices
        self.assertEqual(choices, Ticket.Type.choices) 
    
    def test_type_default(self):
        default_type = Ticket._meta.get_field("type").default
        self.assertEqual(default_type, Ticket.Type.EARLY_BIRD)
        
    def test_type_early_bird(self):
        # Test that the type can be set to EARLY_BIRD
        ticket = Ticket.objects.create(
            event=self.event,
            order=self.order,
            type="EARLY_BIRD"
        )
        self.assertEqual(ticket.type, Ticket.Type.EARLY_BIRD)
    
    def test_type_standard(self):
        # Test that the type can be set to STANDARD
        ticket = Ticket.objects.create(
            event=self.event,
            order=self.order,
            type="STANDARD"
        )
        self.assertEqual(ticket.type, Ticket.Type.STANDARD)
        
    def test_get_tickets_by_event(self):
        # Test that 2 early bird tickets of the default event have been issued.
        tickets = Ticket.get_tickets_by_event(self.event)
        self.assertEqual(tickets.count(), 2)
        for ticket in tickets:
            self.assertEqual(ticket.event, self.event)
            self.assertEqual(ticket.type, 'early_bird')
        
    def test_get_tickets_by_order(self):
        # Test that the default order contains 2 early bird tickets.
        tickets = Ticket.get_tickets_by_order(self.order)
        self.assertEqual(tickets.count(), 2)
        for ticket in tickets:
            self.assertEqual(ticket.order, self.order)
            self.assertEqual(ticket.type, 'early_bird')