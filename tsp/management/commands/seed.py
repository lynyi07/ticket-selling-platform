from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from faker import Faker
from tsp.models import Domain, University, Student, StudentUnion, Society, Event, Order, EventCartItem, Cart
import pandas as pd
import random
from datetime import timedelta, datetime
from django.utils import timezone
from ticket_selling_platform import settings
import stripe
import time

stripe.api_key = settings.STRIPE_SECRET_KEY

class Command(BaseCommand):
    """Command to seed the database."""

    PASSWORD = "Password123"
    DATAFRAME = pd.read_excel("tsp/data/domains.xlsx")
    TIMEZONE = timezone.get_current_timezone()
    print("Data frame loaded successfully")

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self._create_accounts()
        print("Domains, Universities, and Students seeding complete")
        print("Seed complete")

    def _create_accounts(self):
        """Create all objects in the database."""
        stripe_account = self._create_stripe_account()
        self._accept_stripe_terms(stripe_account)
        chosen_universities = Command.DATAFRAME.iloc[[5,6,9,11]] # Loads KCL, UCL, QMU, and LSE
        for university_name, domain, abbreviated_name in zip(chosen_universities['University'], chosen_universities['Domain'], chosen_universities['Abbreviated Name']):
            try: 
                if(University.objects.filter(name = university_name).exists()):
                    university = University.objects.get(name = university_name)
                else:
                    university = self._create_university(university_name, abbreviated_name)
                    self._create_student_accounts(university, domain, 20)
                    student_union = self._create_student_union_account(university, abbreviated_name, domain)
                    if abbreviated_name == 'KCL':
                        self._create_default_student()
                        self._create_default_society(stripe_account)
                    self._create_society_accounts(student_union, abbreviated_name, domain, stripe_account, 4)
                    
                self._create_domain(domain, university)

            except IntegrityError as e:
                print("An error occurred while seeding the data:", e)
        self._create_events()
        self._create_orders()

    def _create_university(self, name_in, abbreviation_in):
        """
        Create a University object in the database.

        Parameters:
        -------
        name_in : str
            The university's name.
        abbreviation_in : str
            The university's abbreviated name.
        
        Returns:
        -------
        university
            The newly created University.
        """

        return University.objects.create(
            name = name_in,
            abbreviation = abbreviation_in
        )
    
    def _create_domain(self, domain_in, university_in):
        """
        Create a Domain object in the database.

        Parameters:
        -------
        domain_in : str
            The university's domain.
        university_in : object
            The university.
        """

        Domain.objects.create(
            university = university_in,
            name = domain_in
        )

    def _create_student_union_account(self, university_in, abbreviation_in, domain_in):
        """
        Create a Student Union object in the database.

        Parameters:
        -------
        university_in : object
            The university.
        abbreviation_in : str
            The university's abbreviated name.
        domain_in : str
            The university's domain.
        
        Returns:
        -------
        student union
            The newly created Student Union.
        """

        return StudentUnion.objects.create_user(
            email = f'{abbreviation_in.lower()}su@{domain_in}',
            password = Command.PASSWORD,
            name = f'{abbreviation_in}SU',
            university = university_in,
            role = 'STUDENT_UNION',
            is_superuser = True
        )

    def _create_society_accounts(self, student_union_in, abbreviation_in, domain_in, stripe_account_in, count_in):
        """
        Create a given number of Society objects in the database.

        Parameters:
        -------
        student_union_in : object
            The Student Union.
        university_in : object
            The university.
        abbreviation_in : str
            The university's abbreviated name.
        domain_in : str
            The university's domain.
        stripe_account_in : object
            The stripe account for the payments
        count_in : int
            The number of society objects to create.
        """

        students_in_same_university = list(Student.objects.filter(university=student_union_in.university).all())
        for i in range(count_in):
            student = random.sample(students_in_same_university, k=1)[0]
            society = Society.objects.create_user(
                email = f'society.{i}@{domain_in}',
                password = Command.PASSWORD,
                student_union = student_union_in,
                name = f'{abbreviation_in} society.{i}',
                member_discount = round(random.uniform(5,10), 2),
                member_fee = round(random.uniform(5,10), 2),
                university = student_union_in.university,
                role = 'SOCIETY',
                is_superuser = False,
                account_number = '00012345',
                sort_code = '040004',
                account_name = f'{student.first_name} {student.last_name}',
                stripe_account_id = f'{stripe_account_in.id}'
            )

            for student in random.sample(students_in_same_university, k=random.randint(4,10)):
                society.add_follower(student)

            for student in random.sample(students_in_same_university, k=random.randint(4,10)):
                society.add_subscriber(student)

            for student in random.sample(students_in_same_university, k=random.randint(3,10)):
                society.add_regular_member(student)

            for student in random.sample(students_in_same_university, k=random.randint(3,7)):
                if student not in list(society.regular_member.all()):
                    society.add_committee_member(student)

    def _create_student_accounts(self, university_in, domain_in, count_in):
        """
        Create a given number of Student objects in the database.

        Parameters:
        -------
        university_in : university
            The given university.
        domain_in : str
            The university's domain.
        count_in : int
            The number of student objects to create.
        """

        for i in range(count_in):
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            email = f'student.{i}@{domain_in}'
            Student.objects.create_user(
                email = email,
                password = Command.PASSWORD,
                first_name = first_name,
                last_name = last_name,
                university = university_in,
                role = "STUDENT",
                is_superuser = False
            )

    def _create_events(self):
        """Create a random number of Event objects for each society in the database."""

        societies = Society.objects.all()
        for society in societies:
            for i in range(random.randint(1,20)):
                start_date = self.faker.date_time_between(start_date='-1y', end_date='+120d').replace(tzinfo=Command.TIMEZONE)
                end_date = (start_date + timedelta(hours=random.randint(2,8))).replace(tzinfo=Command.TIMEZONE)
                early_booking_capacity = random.randint(0,30)
                standard_booking_capacity = random.randint(early_booking_capacity, early_booking_capacity + 20)
                if random.random() > 0.9:
                    status = 'CANCELLED' 
                else:
                    status = 'ACTIVE'
                event = Event.objects.create(
                    host = society,
                    name = f'event.{i}',
                    description = self.faker.sentence(),
                    location = self.faker.address(),
                    start_time = start_date,
                    end_time = end_date,
                    early_booking_capacity = early_booking_capacity,
                    standard_booking_capacity = standard_booking_capacity,
                    early_bird_price = round(random.uniform(1,4), 2), 
                    standard_price = round(random.uniform(5,10), 2),
                    status = status,
                    photo = '/static/images/default_event_photo.jpg'
                )
                if random.random() > 0.9:
                    societies_in_event = random.sample(list(societies), k=random.randint(1,5))
                    for other_society in societies_in_event:
                        event.society.add(other_society)
                event.society.add(society)

    def _create_orders(self):
        """Create a random number of Order objects for each student in the database."""

        for student in Student.objects.all():
            cart = Cart.objects.create(student=student)
            address = self.faker.address().split('\n')
            for i in range(random.randint(1,4)):
                create_at = (datetime.now() - timedelta(days=random.randint(1,350))).replace(tzinfo=Command.TIMEZONE)
                self._add_items_to_cart(cart, create_at, student)

                Order.objects.create(
                    student = student,
                    customer_id = "fakecus_" + self.faker.sha1(),
                    create_at = create_at,
                    line_1 = address[0],
                    line_2 = address[1],
                    city_town = address[-2],
                    postcode = address[-1],
                    country = 'United Kingdom'
                )   
    
    def _add_items_to_cart(self, cart_in, create_at_in, student_in):
        """
        Adds a random number of events and a selected number of memberships to the cart.

        Parameters:
        -------
        cart_in : Cart
            The student's cart object.
        create_at_in : datetime
            The date the order was created in order to filter for events after that.
        student_in : Student
            The student object
        """

        events = random.sample(list(Event.objects.filter(start_time__gt=create_at_in, status='ACTIVE', society__university=student_in.university).all()), k=random.randint(1,3))

        event_cart_items = []
        for event in events:
            event_cart_items.append(self._create_event_cart_item(event))

        for event_cart_item in event_cart_items:
                cart_in.event_cart_item.add(event_cart_item)

        if not Order.objects.filter(student=cart_in.student).exists():
            memberships = list(Society.objects.filter(regular_member=cart_in.student).all())
            for membership in memberships:
                cart_in.membership.add(membership)

    def _create_event_cart_item(self, event_in):
        """
        Create the event cart item with the given event.

        Parameters:
        -------
        event_in : Event
            The event object.
        """

        return EventCartItem.objects.create(
            event=event_in,
            early_bird_quantity = random.randint(1,3),
            standard_quantity = 0,
        )

    def _create_default_student(self):
        """Create the default student account"""

        university = University.objects.get(name="King's College London")
        Student.objects.create_user(
            email='joe.doe@kcl.ac.uk',
            password=Command.PASSWORD,
            first_name='Joe',
            last_name='Doe',
            university=university,
            role = "STUDENT",
            is_superuser = False
        )
        print(f'Default student seeding complete')

    def _create_default_society(self, stripe_account_in):
        """Create the default society account"""
        university = University.objects.get(name="King's College London")
        students_in_same_university = list(Student.objects.filter(university=university).all())
        student = random.sample(students_in_same_university, k=1)[0]
        society = Society.objects.create_user(
            email='robotics@kcl.ac.uk',
            password=Command.PASSWORD,
            student_union = StudentUnion.objects.get(email='kclsu@kcl.ac.uk'),
            name = 'Robotics',
            member_discount = round(random.uniform(5,10), 2),
            member_fee = round(random.uniform(5,10), 2),
            university = university,
            role = 'SOCIETY',
            is_superuser = False,
            account_number = '00012345',
            sort_code = '040004',
            account_name = f'{student.first_name} {student.last_name}',
            stripe_account_id = f'{stripe_account_in.id}'
        )

        for student in random.sample(students_in_same_university, k=random.randint(4,10)):
            society.add_follower(student)

        for student in random.sample(students_in_same_university, k=random.randint(4,10)):
            society.add_subscriber(student)

        for student in random.sample(students_in_same_university, k=random.randint(3,10)):
            society.add_regular_member(student)

        for student in random.sample(students_in_same_university, k=random.randint(3,7)):
            if student not in list(society.regular_member.all()):
                society.add_committee_member(student)

        print(f'Default society seeding complete')

    def _create_stripe_account(self):
        """
        Create the Stripe account for all the seeded societies.

        Returns
        -------
        stripe.Account
            The Stripe account created.
        """

        account = stripe.Account.create(
            type='custom',
            country='GB',
            email='test@kcl.ac.uk',
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
                'email': 'test@kcl.ac.uk',
                'first_name': 'John',
                'last_name': 'Doe',
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
                'routing_number': '040004',
                'account_number': '00012345',
                'account_holder_name': 'John Doe',
            },
        )
        return account

    def _accept_stripe_terms(self, account):
        """
        Accept the terms of service for the seller's account
        
        Parameters
        ----------
        account : stripe.Account
            The society's Stripe account.
        """
        
        account.tos_acceptance = {
            'date': int(time.time()),
            'ip': '108.180.128.41',
        }
        account.save()