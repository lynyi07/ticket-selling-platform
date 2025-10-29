# Ticket Selling Platform (Tixstar)

A full-stack web application that enables university students to discover, manage and purchase society event tickets online. Supports different user roles including students, societies and university student union administrators.


## Overview

This platform is built to streamline university society engagement by providing a unified digital space for event discovery and ticketing. Students can browse events, follow societies, save favourites and manage purchases. Societies can publish and manage events including ticketing and membership details. The student union can verify and onboard official societies to ensure authenticity and secure participation.

This project demonstrates full stack development including authentication flows, database modelling, role-based access control and third-party payment integration.


## Platform Features

The platform supports three different user roles with distinct access privileges and functionality: Student, Society, and Student Union Administrator.

### Student Features

Students are the primary users purchasing tickets and interacting with societies.

They can:
- Create a verified student account using a university email domain
- Browse personalised and recommended events
- Follow societies and view related activity on a For You page
- View detailed event pages and add tickets or memberships to cart
- Manage cart items before checkout
- Complete secure checkout with test payment functionality
- Receive confirmation emails for orders
- View order history, order details, and purchased tickets
- Perform password updates and account recovery

Restrictions:
- Cannot access society or administrator functionality

### Society Features

Societies are event organisers and membership providers.

They can:
- View and manage society profiles and bank details
- Create new events with partner societies
- Notify subscribers when new events are created
- Manage event status: upcoming, past and cancelled events
- Modify details of upcoming events including capacity and booking settings
- View ticket holders and membership lists
- Manage membership fees and discounts

Restrictions:
- Cannot access student union functions

### Student Union Administrator Features

Admins provide organisational governance.

They can:
- Approve and create societies in the database
- Review and manage society details
- Perform password recovery and secure logout

Restrictions:
- No access to event creation or student-specific features


## Tech Stack

- Python (Django)
- HTML, CSS, JavaScript
- SQLite or PostgreSQL database
- Stripe payment API (test mode)
- Automated testing with coverage.py


## How To Run Locally
1. Clone the repository:
```bash
git clone https://github.com/<your-username>/ticket-selling-platform
cd ticket-selling-platform
```

2. Create and activate a virtual environment:
```bash
virtualenv venv
source venv/bin/activate
```

3. Install all required packages:
```bash
pip3 install -r requirements.txt
```

4. Apply all database migrations:
```bash
python3 manage.py migrate
```

5. Seed the development database with initial data:
```bash
python3.manage.py seed
```

6. (Optional) Run automated tests to verify the system:
```bash
python3 manage.py test
```

7. Start the local development server:
```bash
python3 manage.py runserver
```

8. Once the server is running, the application will be accessible at:
```
http://127.0.0.1:8000/
```

## Demo

Watch a walk-through demo on YouTube: 
https://www.youtube.com/watch?v=f5rX38wraUE


## Contributors
This project was developed collaboratively by:
- Lyn Yi Cheng
- Simran Debnath
- Daniel Holland
- Brian Jalleh
- Susetta James
- Seohyun (Jen) Kwon
- Jasdeep Panum
- Erikas Staugas
- Yue (Michelle) Wang

