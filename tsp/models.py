import os
from ticket_selling_platform import settings
from django.core.validators import RegexValidator
from django.core.validators import MinLengthValidator
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from collections import defaultdict
from django.db.models import Sum
from decimal import Decimal
import json
from django.utils.functional import cached_property
from tsp.managers import (
    CustomUserManager,
    StudentManager,
    SocietyManager,
    StudentUnionManager,
)

class University(models.Model):
    """
    University model used to ensure only students can register.

    Attributes
    ----------
    name : models.CharField
        Name of the given university.
    abbreviation : models.CharField
        Abbreviation of the university name.
    """

    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=50)

    @property
    def domains(self):
        """
        Get domains associated with the given university.

        Returns
        -------
        QuerySet
            A QuerySet of domain objects associated with the given university.
        """

        return self.domain_set.all()
    

class Domain(models.Model):
    """
    Domain model used to represent a domain of a university.

    Attributes
    ----------
    university: models.ForeignKey
        University that owns the given domain.
        A domain belongs to a single university and the university can have
        multiple domains.
    name : models.CharField
        Name of the given domain.
    """

    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='domains'
        )
    name = models.CharField(max_length=50)


class User(AbstractBaseUser, PermissionsMixin):
    """
    User model class responsible for handling all base user related logic

    Attributes
    ----------
    university : models.ForeignKey
        The university of the given user.
    email : models.EmailField
        Email used to log into the platform.
    is_superuser : models.BooleanField
        Boolean flag indicating if the user has superuser access control.
    role : Role
        Enum value indicating the role and access control of the given user.
    """

    class Role(models.TextChoices):
        STUDENT_UNION = 'STUDENT_UNION', 'Student Union'
        SOCIETY = 'SOCIETY', 'Society'
        STUDENT = 'STUDENT', 'Student'

    university = models.ForeignKey(University, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(('email address'), unique=True)
    is_superuser = models.BooleanField(default=False)
    role = models.CharField(
        choices=Role.choices, max_length=50, default='STUDENT'
    )
    objects = CustomUserManager()
    default_choice = 'STUDENT'
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    def __str__(self) -> str:
        """
        Display a user friendly format of the user.

        Returns
        -------
        str
            A string representation of the user object.
        """

        return f'{self.role}({self.email}, {self.password})'


class Student(User):
    """
    Student model represents a student user of the university, upon
    creation of the user the role will automatically be assigned to
    STUDENT.

    Attributes
    ----------
    saved_event : models.ManyToManyField
        The event that the given student is interested in.
    purchased_event : models.ManyToManyField
        The event that the given student has purchased. 
    discounted_event : models.ManyToManyField
        The event that the given student has purchased with discount applied.
    first_name : models.CharField
        First name of the given student.
    last_name : models.CharField
        Last name of the given student.
    """

    saved_event = models.ManyToManyField(
        'Event', 
        blank=True,
        related_name='saved_event'
    )
    purchased_event = models.ManyToManyField(
        'Event', 
        blank=True, 
        related_name='purchased_event'
    )
    discounted_event = models.ManyToManyField(
        'Event', 
        blank=True, 
        related_name='discounted_event'
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    student = StudentManager()

    def save(self, *args, **kwargs) -> None:
        self.role = User.Role.STUDENT
        return super().save(*args, **kwargs)
    
    def save_event(self, event):
        """
        Save the given event.

        Parameters
        ----------
        event : Event
            The event to save.
        """
        
        self.saved_event.add(event)
        
    def unsave_event(self, event):
        """
        Unsave the given event.

        Parameters
        ----------
        event : Event
            The event to unsave.
        """
        
        self.saved_event.remove(event)

    def event_saved(self, event):
        """
        Check if the given event has been saved.

        Parameters
        ----------
        event : Event
            The event to check.

        Returns
        -------
        bool
            True if the event has been saved, False otherwise.
        """

        return event in self.saved_event.all()

    def purchase_event(self, event):
        """
        Purchase the given event.

        Parameters
        ----------
        event : Event
            The event to purchase.
        """
        
        self.purchased_event.add(event)
    
    def purchase_discounted_event(self, event):
        """
        Purchase the given event.

        Parameters
        ----------
        event : Event
            The event to purchase.
        """
        
        self.discounted_event.add(event)
    
    def event_discounted(self, event):
        """
        Check if the given event has been purchased with discount applied.

        Parameters
        ----------
        event : Event
            The event to check.

        Returns
        -------
        bool
            True if the event has been purchased with discount applied, 
            False otherwise.
        """
        
        return event in self.discounted_event.all()
    
    @property
    def full_name(self) -> str:
        """
        Concatenate the user's first name and last name.

        Returns
        -------
        str
            The user's full name.
        """
        return f'{self.first_name} {self.last_name}'


class StudentUnion(User):
    """
    StudentUnion model represents a student union of the university,
    upon creation of the user the role will automatically be assigned
    to STUDENT_UNION.

    Attributes
    ----------
    name : models.CharField
        Name of the given student union.
    """

    name = models.CharField(max_length=50)
    student_union = StudentUnionManager()

    def save(self, *args, **kwargs) -> None:
        if self.role is self.default_choice:
            self.role = User.Role.STUDENT_UNION
            self.is_superuser = True
        return super().save(*args, **kwargs)


class Society(User):
    """
    Society model represents a society of the university, upon creation
    of the user the role will automatically be assigned to SOCIETY.

    Attributes
    ----------
    student_union : models.ForeignKey
        The student union that manages the given society.
    name : models.CharField
        Name of the given society.
    follower : models.ManyToManyField
        The student who is a follower of the given society. 
    subscriber : models.ManyToManyField
        The student who is in the society's mailing list.
    regular_member : models.ManyToManyField
        The student who is a regular member of the given society.
    committee_member : models.ManyToManyField
        The student who is a committee member of the given society.
    member_discount : models.DecimalField
        Member discount for the given society's event tickets.
    member_fee : models.DecimalField
        Member fee for one academic year of the given society.
    account_number : models.CharField
        The bank account number of the given society.
    sort_code : models.CharField
        The sort code of the given society.
    stripe_account_id : models.CharField
        The id of the stripe account that is associated with the given society.
    """

    student_union = models.ForeignKey(StudentUnion, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    follower = models.ManyToManyField(
        Student,
        related_name='follower',
        blank=True
    )
    subscriber = models.ManyToManyField(
        Student,
        related_name='subscriber',
        blank=True
    )
    regular_member = models.ManyToManyField(
        Student,
        related_name='regular_member',
        blank=True
    )
    committee_member = models.ManyToManyField(
        Student,
        related_name='committee_members',
        blank=True
    )
    member_discount = models.DecimalField(
        default=0.0,
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    ) 
    member_fee = models.DecimalField(
        default=0.0,
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )
    account_number = models.CharField(
        max_length=8,
        validators=[
            MinLengthValidator(8),
            RegexValidator(
                regex='^\d{0,8}$',
                message='Account number must be 8 digits.',
                code='invalid_account_number'
            )
        ],
        blank=True,
        null=True
    )
    sort_code = models.CharField(
        max_length=6,
        validators=[
            MinLengthValidator(6),
            RegexValidator(
                regex='^\d{0,6}$',
                message='Sort code must be 6 digits.',
                code='invalid_sort_code'
            )
        ],
        blank=True,
        null=True
    )
    account_name = models.CharField(
        max_length=50,
        blank=True, 
        null=True
    )
    stripe_account_id = models.CharField(max_length=50, blank=True, null=True)
    society = SocietyManager()

    def save(self, *args, **kwargs) -> None:
        if self.role is self.default_choice:
            self.role = User.Role.SOCIETY
        return super().save(*args, **kwargs)
    
    @property
    def followers(self):
        """
        Get all the followers of the society.

        Returns
        -------
        QuerySet
            A QuerySet containing all the followers of the society.
        """
    
        return self.follower.all()
    
    @property
    def subscribers(self):
        """
        Get all the subscribers of the society.

        Returns
        -------
        QuerySet
            A QuerySet containing all the subscribers of the society.
        """
    
        return self.subscriber.all()
    
    @property
    def regular_members(self):
        """
        Get all the regular members of the society.

        Returns
        -------
        QuerySet
            A QuerySet containing all the regular members of the society.
        """
    
        return self.regular_member.all()
    
    @property
    def committee_members(self):
        """
        Get all the committee members of the society.

        Returns
        -------
        QuerySet
            A QuerySet containing all the committee members of the society.
        """
    
        return self.committee_member.all()
    
    @property
    def upcoming_events(self):
        """
        Get a QuerySet of upcoming events.

        Returns:
        ----------
        QuerySet
            A QuerySet of upcoming events.
        """
    
        now = timezone.now()
        events = Event.objects.filter(society=self, end_time__gte=now, status='ACTIVE')
        return events
    
    @property
    def most_upcoming_event(self):
        """
        Get the next upcoming event.

        Returns:
        ----------
        Event or None
            The next upcoming event or None if there are no upcoming events.
        """
        events = self.upcoming_events
        if events:
            return events.order_by('start_time').first()
        else:
            return None
    
    @property
    def past_events(self):
        """
        Get a QuerySet of past events.

        Returns:
        ----------
        QuerySet
            A QuerySet of past events.
        """
        
        now = timezone.now()
        events = Event.objects.filter(society=self, end_time__lt=now, status='ACTIVE')
        return events

    @property
    def cancelled_events(self):
        """
        Get a QuerySet of cancelled events.

        Returns:
        ----------
        QuerySet
            A QuerySet of cancelled events.
        """
        
        events = Event.objects.filter(society=self, status='CANCELLED')
        return events

    @property
    def has_bank_details(self):
        """
        Check if the society has provided bank details.

        Returns:
        ----------
        bool
            True if the society has bank details, False otherwise.
        """

        return (
            self.stripe_account_id 
            and self.account_number 
            and self.account_name 
            and self.sort_code
        )
        
    @property
    def accept_new_member(self):
        """
        Check if the society is accepting new members.

        Returns:
        ----------
        bool
            True if the society is accepting new members, False otherwise.
        """
        
        return not self.member_fee or self.has_bank_details 
    
    def is_student_member(self, student):
        """
        Check if a given student is a member (either regular or committee) 
        of the society.
        
        Parameters
        ----------
        student : Student
            The student to check membership for.
            
        Returns
        -------
        bool
            True if the student is a member of the society, False otherwise.
        """
    
        return (
            student in self.committee_members or 
            student in self.regular_members
        )
    
    def add_follower(self, student):
        """
        Add a student to the society's followers.
        
        Parameters
        ----------
        student : Student
            The student to add.
        """
        self.follower.add(student)
    
    def add_subscriber(self, student):
        """
        Add a student to the society's subscribers.
        
        Parameters
        ----------
        student : Student
            The student to add.
        """
        
        self.subscriber.add(student)

    def add_regular_member(self, student):
        """
        Add a student to the society's regular members.
        
        Parameters
        ----------
        student : Student
            The student to add.
        """
        
        self.regular_member.add(student)

    def add_committee_member(self, student):
        """
        Add a student to the society's committee members.
        
        Parameters
        ----------
        student : Student
            The student to add.
        """
        
        self.committee_member.add(student)

    def remove_committee_member(self, student):
        """
        Remove the student from the society's committee members.
        
        Parameters
        ----------
        student : Student
            The student to remove.
        """
        
        self.committee_member.remove(student)

    def remove_follower(self, student):
        """
        Remove the student from the society's followers.
        
        Parameters
        ----------
        student : Student
            The student to remove.
        """
        
        self.follower.remove(student)

    def remove_subscriber(self, student):
        """
        Remove the student from the society's subscribers.
        
        Parameters
        ----------
        student : Student
            The student to remove.
        """
        
        self.subscriber.remove(student)

    def get_subscribers_email_list(self):
        """
        Get a list of subscriber emails.

        Returns:
        ----------
        List
            A list of subscriber emails.
        """
    
        subscribers = self.subscriber.all()
        return [(student.email) for student in subscribers]
    

class Event(models.Model):
    """
    Event model represents an event held by one or more societies.

    Attributes
    ----------
    host : models.ForeignKey
        The society that hosts the given event.
        All proceeds from ticket sales will be sent to the bank account of 
        the host society for distribution.
    society : models.ManyToManyField
        The one or many societies that hold the given event. This includes 
        the host and the partners. 
    name : models.CharField
        The name of the given event.
    description : models.CharField
        The description of the given event that contains an introduction
        or any relevant information.
    photo : models.ImageField
        The photo of the given event. A default photo is used unless the
        event photo is set otherwise.
    location : models.CharField
        The location of the given event.
    start_time : models.DateTimeField
        The date and time indicating when the given event starts.
    end_time : models.DateTimeField
        The date and time indicating when the given event ends.
    early_booking_capacity : models.IntegerField
        The capacity of early bird tickets for the given event.
    standard_booking_capacity : models.IntegerField
        The capacity of standard booking tickets for the given event.
    early_bird_price : models.DecimalField
        The price of the early bird event ticket.
    standard_price : models.DecimalField
        The price of the standard event ticket.
    status : Status
        Enum indicating the status of the given event.
    """

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        CANCELLED = 'CANCELLED', 'Cancelled'

    host = models.ForeignKey(
        Society,
        related_name='host',
        on_delete=models.DO_NOTHING,
        null=True, 
        blank=True
    )
    society = models.ManyToManyField(
        Society,
        related_name='society',
    )
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=5000, null=True, blank=True)
    photo = models.ImageField(
        upload_to='events/',
        default=os.path.join(settings.MEDIA_ROOT, 'default_event_photo.jpg'),
        blank=False,
    )
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    early_booking_capacity = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    standard_booking_capacity = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    early_bird_price = models.DecimalField(
        default=0.0,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )
    standard_price = models.DecimalField(
        default=0.0,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    class Meta:
        ordering = ['start_time']
        
    def cancel_event(self):
        """Set the event status to cancelled."""
        
        self.status = self.Status.CANCELLED
    
    @property
    def is_active(self):
        """
        Get if the event is active.
        
        Returns
        -------
        bool
            Return true if the event is active. False otherwise.
        """
        return (
            self.status == self.Status.ACTIVE and
            self.end_time > timezone.now()
        )

    @staticmethod
    def get_event_ticket_inventory(event, ticket_type):
        """
        Get the current inventory of the specified ticket type for the event.

        Parameters
        ----------
        event : Event
            The given event that issues the ticket. 
        ticket_type : str
            The type of ticket to get the inventory for. Must be either 
            "early_bird" or "standard".

        Returns
        -------
        int
            The current inventory of the specified ticket type for the event.
        """
        
        inventory = 0
        if event:
            # Get the booking capacity of the specified ticket type
            if ticket_type not in ('early_bird', 'standard'):
                raise ValueError("Invalid ticket type specified.")
            if ticket_type == 'early_bird':
                booking_capacity = event.early_booking_capacity
            else:
                booking_capacity = event.standard_booking_capacity
                
            # Get the number of tickets sold for the event of the specified 
            # ticket type
            tickets_sold = Ticket.objects.filter(
                event=event,
                type=ticket_type,
            ).count()
            inventory = booking_capacity - tickets_sold 
        return inventory
    
    @property
    def event_savers(self):
        """
        Get a list of students who saved the current event.

        Returns
        -------
        QuerySet
            A QuerySet of Student objects who saved the event.
        """
        
        return Student.objects.filter(saved_event=self)
    
    @property
    def event_buyers(self):
        """
        Get a list of students who purchased the current event.

        Returns
        -------
        QuerySet
            A QuerySet of Student objects who purchased the event.
        """
        
        return Student.objects.filter(purchased_event=self)
    
    @property
    def event_filtered_savers(self):
        """
        Get a list of students who only saved the current event and has not 
        purchased the ticket.

        Returns
        -------
        QuerySet
            A QuerySet of Student objects who only saved the event.
        """
        
        buyers = self.event_buyers
        savers = self.event_savers
        filtered_savers = [s for s in savers if s not in buyers]  
        return list(filtered_savers)
        
    def is_organiser(self, society):
        """
        Check if the given society is an organiser of the current event.

        Parameters
        ----------
        society : Society
            The society object to check if it's an organiser of the event.

        Returns
        -------
        bool
            True if the given society is an organiser of the event, False otherwise.
        """
        
        return society in self.society.all()

        
class EventCartItem(models.Model):
    """
    EventCartItem model represents the specific event that can be added to the 
    shopping cart.
    
    Attributes
    ----------
    event : models.ForeignKey
        The event that the event cart item is associated with.
        For each user, one event can only be associated with one event cart item.
    early_bird_quantity : models.IntegerField
        The number of early bird tickets of the associated event in one user's 
        cart.
    standard_quantity : models.IntegerField
        The number of standard tickets of the associated event in one user's 
        cart.
    """
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    early_bird_quantity = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0)],
    )
    standard_quantity = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0)]
    )
    
    def get_discount_amount(self, discount_rate):
        """
        Get the discount amount if given event cart item is eligible for it.
        
        Parameters:
        -----------
        membership_for_discount : Society
            The society whose membership qualifies for a discount.
        event_cart_item : EventCartItem
            The event cart item to calculate the discount for.
        
        Returns:
        --------
        decimal
            The discount amount applicable for the given event cart item.
        """
        
        early_bird_price = self.event.early_bird_price
        standard_price = self.event.standard_price

        if self.standard_quantity > 0: 
            return round(standard_price * discount_rate, 2)  
        else: 
            return round(early_bird_price * discount_rate, 2)


class BaseCart(models.Model):
    """
    Base cart model represents a shopping cart of a student. This model 
    contains the basic fields that are common to all types of carts.

    Attributes
    ----------
    event_cart_items : models.ManyToManyField
        The event cart items that have been added to the cart.
    membership : models.ManyToManyField
        The membership that have been added to the cart.
    """

    event_cart_item = models.ManyToManyField(EventCartItem, blank=True)
    membership = models.ManyToManyField(Society, blank=True)


class Cart(BaseCart):
    """
    Cart model represents a shopping cart of a student with additional 
    methods to calculate cart-related values.

    Attributes
    ----------
    Inherit all attributes from BaseCart model.
    student : models.ForeignKey
        The student that the cart belongs to.
    """
    
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    
    @property
    def all_items_free(self):
        """
        Check if all items in the cart are free.

        Returns
        -------
        bool
            True if all items in the cart are free, False otherwise.
        """
        
        return not self.total_price and self.count
    
    @property
    def total_price(self):
        """
        Get the total price of tickets and memberships in the given cart 
        that is due to pay.
        
        Returns:
        --------
        decimal
            The total price of items in the cart.
        """
        total_price = (
            self.total_ticket_price_before_discount + 
            self.total_membership_price - 
            self.total_saved
        )
        return total_price
    
    @property
    def total_saved(self):
        """
        Get the total discount applied to items in the cart.
        
        Returns:
        --------
        decimal
            The total amount of discount for all items in the cart.
        """
        
        total_saved = Decimal('0.00')
        if self.discount_data:
            for item, discount in self.discount_data.items():
                total_saved += discount
        return total_saved
    
    @property
    def count(self):
        """
        The total number of tickets and memberships in the given cart. 
        
        Returns:
        --------
        int
            The total amount of tickets and memberships in the cart.
        """
        return self.ticket_count + self.membership_count
    
    @property
    def ticket_count(self):
        """
        Get the total amount of tickets that have been added to cart.
        
        Returns:
        --------
        int
            The total amount of tickets in the cart.
        """
        
        ticket_count = 0
        for item in self.event_cart_item.all():
            ticket_count += item.early_bird_quantity + item.standard_quantity
        return ticket_count
    
    @property
    def membership_count(self):
        """
        Get the total amount of memberships that have been added to the cart.
        
        Returns:
        --------
        int
            The total amount of memberships in the cart.
        """
        
        return self.membership.count()
    
    @property
    def total_ticket_price_before_discount(self):
        """
        Get the total price of tickets in the cart before applying membership 
        discount.
        
        Returns:
        --------
        decimal
            The total cost of tickets added to the cart before discount applied.
        """
        
        total_price = Decimal('0.00')
        for item in self.event_cart_item.all():
            early_bird_price = item.event.early_bird_price 
            standard_price = item.event.standard_price
            total_price += early_bird_price * item.early_bird_quantity
            total_price += standard_price * item.standard_quantity
        return total_price 
    
    @property
    def total_membership_price(self):
        """
        Get the total cost of memberships that have been added to the cart.
        
        Returns:
        --------
        decimal
            The total cost of memberships added to the cart.
        """
        
        total_price = Decimal('0.00')
        for membership in self.membership.all():
            total_price += membership.member_fee
        return total_price
    
    @property
    def discount_data(self):
        """
        Get a dictionary mapping event cart item id to the amount of 
        discount applied.
        
        Returns:
        --------
        defaultdict(Decimal)
            A dictionary where the keys are the id of event cart items 
            and the values are the amount of discount applied to them.
        """
        
        discount_data = defaultdict(Decimal)
        for item in self.event_cart_item.all():
            discount_rate = self.get_discount_rate(item)
            discount = item.get_discount_amount(discount_rate)
            discounted = self.student.event_discounted(item.event)
            if discount != 0.0 and not discounted:
                item_id = item.id
                discount_data[item_id] += discount
        return discount_data
    
    def get_discount_rate(self, event_cart_item):
        """
        Get the discount rate applied to the given event cart item.
        If there are more than one membership applicable, return the 
        highest discount rate.
        
        Returns:
        --------
        decimal 
            The highest applicable discount rate for the given event cart item.
        """
        
        event = event_cart_item.event
        discount_rate = Decimal('0.00')
        for society in event.society.all():
            if self.user_is_member(society) or self.membership_is_in_cart(society):
                discount_rate = max(discount_rate, society.member_discount)
        return discount_rate / 100
    
    def membership_is_in_cart(self, membership):
        """
        Get the boolean value indicating whether the given membership has 
        been added to the cart.
        
        Returns:
        --------
        bool 
            True if the given membership has been added to the cart, False 
            otherwise.
        """
        
        memberships_in_cart = self.membership.all()
        return membership and membership in memberships_in_cart
    
    def user_is_member(self, membership):
        """
        Check if the student is already a member of a specific society when 
        adding membership to the cart.
        
        Parameters:
        -----------
        membership: Society
            The membership to be added to the cart.
            
        Returns:
        --------
        bool
            True if the student is a member of the given society, False otherwise.
        """
        
        return membership and self.student in membership.regular_member.all()
    
    def get_ticket_quantity_in_cart_per_event(self, event, ticket_type):
        """
        Get the number of tickets in the user's cart for the specified event.

        Parameters
        ----------
        event : Event
            The event for which the ticket quantity is being calculated.
        ticket_type : str
            The type of ticket being calculated. Should be one of 'early_bird' 
            or 'standard'.

        Returns
        -------
        int
            The number of tickets of the specified type in the user's cart 
            for the specified event.
        """
        
        try:
            event_cart_item = self.event_cart_item.get(event=event)
        except EventCartItem.DoesNotExist:
            return 0
        quantity_type = f'{ticket_type}_quantity'
        quantity_in_cart =  getattr(event_cart_item, quantity_type)
        return quantity_in_cart
        
    def clear(self):
        """Remove all items from the cart, reset cart data."""
        
        self.event_cart_item.clear()
        self.membership.clear()
        
        
class HistoricalCart(BaseCart):
    """
    Historical cart model represents a historical version of a shopping 
    cart that has been checked out. This model is used to keep track of 
    the historical data of the user's shopping cart.

    Attributes
    ----------
    Inherit all attributes from BaseCart model.
    student : models.ForeignKey
        The student that the cart belongs to.
    order : OneToOneField
        The associated of order that has been placed. 
    total_price : models.DecimalField
        The total price of all items in the cart with discounts applied.
    total_saved : models.DecimalField
        The total amount saved through discounts.
    count : models.IntegerField
        The total number of tickets and memberships in the given cart. 
    discount_data : JSONField
        A dictionary field containing the amount of discount applied to 
        each event cart item in the historical cart.
    """
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    total_price = models.DecimalField(
        default=0.0, 
        max_digits=10, 
        decimal_places=2
    )
    total_saved = models.DecimalField(
        default=0.0, 
        max_digits=10, 
        decimal_places=2
    )
    count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    discount_data = models.JSONField(blank=True, null=True)
    
    @cached_property
    def discount_data_dict(self):
        """
        A cached property that returns the discount data associated 
        with a HistoricalCart as a dictionary. The keys of the dictionary
        are converted to integers. The string values are converted
        to Decimal objects.
        """
        
        discount_data_json = json.loads(self.discount_data)
        discount_data = {}
        for item_id, discount in discount_data_json.items():
            discount_data[int(item_id)] = Decimal(discount)
        return discount_data
    
    
class Order(models.Model):
    """
    Order model represents an order placed by a student.

    Attributes
    ----------
    student : models.ForeignKey
        The student that places the given order.
    customer_id : str, optional
        The customer ID of Stripe associeate with this order. 
    create_at : models.DateTimeField
        The date and time indicating when the order is created.
    line_1 : str
        The first line of the address.
    line_2 : str, optional
        The second line of the address (if applicable).
    city_town : str
        The city or town of the address.
    postcode : str
        The postal code of the address.
    country : str, optional
        The country of the address. Default is 'United Kingdom'.
    """

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    customer_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Stripe customer ID"
    )
    create_at = models.DateTimeField(default=timezone.now)
    line_1 = models.CharField(max_length=255, null=False, blank=False)
    line_2 = models.CharField(max_length=255, blank=True, null=True)
    city_town = models.CharField(max_length=255, null=False, blank=False)
    postcode = models.CharField(max_length=10, null=False, blank=False)
    country = models.CharField(
        max_length=255, 
        default='United Kingdom', 
        null=False, 
        blank=False
    )

    @staticmethod
    def get_orders_by_student(student):
        """
        Get orders for a given student.

        Parameters
        ----------
        student : student
            The given student.

        Returns
        -------
        QuerySet
            Orders for a given student in descending order.
        """
        orders = Order.objects.filter(student=student.id)
        return orders.order_by('-create_at')

    class Meta:
        ordering = ['-create_at']


class Payment(models.Model):
    """
    Payment model represents a payment made by a student. 
    Payment method supports Visa, Mastercard, American Express 
    and China UnionPay payments from customers worldwide.

    Attributes
    ----------
    student : models.ForeignKey
        The student that makes the given payment.
    order : models.OneToOneField
        The order fulfilled by the given payment.
    amount : models.DecimalField
        The amount of the given payment.
    status : Status
        Enum indicating the status of the given order.
    last4 : str
        The last 4 digits of the bank card used for the payment.
    brand : str
        The brand of the bank card used for the payment.
    transaction_id : str 
        The ID of the transaction associated with the payment that is 
        provided by Stripe.  
    """

    class Status(models.TextChoices):
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(
        default=0.0, 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.COMPLETED
    )
    last4 = models.CharField(
        max_length=4,
        blank=True,
        verbose_name="Last 4 digits of bank card"
    )
    brand = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    

class Ticket(models.Model):
    """
    Ticket model represents a ticket for an event.
    Tickets are issued after orders are completed.

    Attributes
    ----------
    event : models.ForeignKey
        The event that issues the given ticket.
    order : models.ForeignKey
        The order that purchases the given ticket. 
    type : models.CharField
        The type of the ticket, either EarlyBird or Standard.
    """
    
    class Type(models.TextChoices):
        EARLY_BIRD = 'EARLY_BIRD', 'early_bird'
        STANDARD= 'STANDARD', 'standard'

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, null=True, blank=True)
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.EARLY_BIRD,
    )

    @staticmethod   
    def get_tickets_by_event(event):
        """
        Get issued tickets for a given event.

        Parameters
        ----------
        event : event
            The given event.

        Returns
        -------
        QuerySet
            Tickets that have been issued for a given event.
        """

        tickets = Ticket.objects.filter(event=event)
        return tickets

    @staticmethod
    def get_tickets_by_order(order):
        """
        Retrieve all tickets associated with a completed order.

        Parameters
        ----------
        order : Order
            The given order to retrieve tickets for.

        Returns
        -------
        tickets : QuerySet or None
            A QuerySet containing the Ticket objects associated with the
            specified order.
        """
    
        tickets = Ticket.objects.filter(order=order)
        return tickets