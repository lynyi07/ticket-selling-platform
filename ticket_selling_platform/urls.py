"""ticket selling platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from tsp.views import (
    landing_page_view, log_out_view, login_view, sign_up_view,
    change_password_view, forgot_password_view,
)
from tsp.views.student import (
    for_you_page_view, all_societies_view, all_events_view, society_page_view,
    follow_society_view, subscribe_society_view, buy_membership_view, 
    event_page_view, save_event_view, add_to_cart_view, cart_detail_view,
    update_cart_view, checkout_view, order_detail_view, ticket_view, 
    order_history_list_view,
)
from tsp.views.society import (
    create_event_view, modify_event_view, cancel_event_view, events_list_view,
    event_detail_view, member_discount_view, member_fee_view, regular_member_list_view,
    committee_member_list_view, committee_member_add_view, committee_member_remove_view,
    contact_committee_members_view, edit_profile_page_view, bank_details_view,
    event_tickets_view, followers_list_view, subscriber_list_view,
    clear_regular_members_view
)
from tsp.views.student_union import (
    societies_view, create_society_view, delete_society_view, society_profile_view
)

urlpatterns = [
    #General
    path('', landing_page_view.LandingPageView.as_view(), name="landing"),
    path('sign_up/', sign_up_view.SignUpView.as_view(), name='sign_up'),
    path('login/', login_view.LogInView.as_view(), name="login"),
    path('log_out/', log_out_view.LogOutView.as_view(), name='log_out'),
    path('forgot_password/', forgot_password_view.ForgetPasswordView.as_view(), name='forgot_password'),
    path('forgot_password_next/<uidb64>', forgot_password_view.ChangePassword.as_view(), name='forgot_password_next'),
    path('change_password/', change_password_view.ChangePasswordView.as_view(), name='change_password'),
    path('activate/<uidb64>/<token>', sign_up_view.activate, name='activate'),

    #Student Union
    path('create_society/', create_society_view.CreateSocietyView.as_view(), name='create_society'),
    path('view_societies/', societies_view.SocietiesView.as_view(), name='view_societies'),
    path('delete_society/', delete_society_view.DeleteSocietyView.as_view(), name='delete_society'),
    path('society_profile/<int:pk>/', society_profile_view.SocietyProfileView.as_view(), name='society_profile'),

    #Society
    path('create_event/', create_event_view.CreateEventView.as_view(), name='create_event'),
    path('events_list/', events_list_view.EventListView.as_view(), name='events_list'),
    path('event_detail/<int:pk>/', event_detail_view.EventDetailView.as_view(), name='event_detail'),
    path('modify_event/<int:pk>/', modify_event_view.ModifyEventView.as_view(), name='modify_event'),
    path('cancel_event', cancel_event_view.CancelEventView.as_view(), name='cancel_event'),
    path('list_committee_member/',committee_member_list_view.ListCommitteeMembersView.as_view(), name='list_committee_member'),
    path('add_committee_member/', committee_member_add_view.AddCommitteeMemberView.as_view(), name='add_committee_member'),
    path('remove_committee_member/', committee_member_remove_view.RemoveCommitteeMemberView.as_view(), name='remove_committee_member'),
    path('list_regular_member/', regular_member_list_view.ListRegularMembers.as_view(), name='list_regular_member'),
    path('member_discount/', member_discount_view.MemberDiscountView.as_view(), name='member_discount'),
    path('member_fee/', member_fee_view.MemberFeeView.as_view(), name='member_fee'),
    path('contact_committee_members/', contact_committee_members_view.ContactCommitteeMembersView.as_view(), name='contact_committee'),
    path('edit_profile_page/',edit_profile_page_view.EditProfilePageView.as_view(), name='edit_profile_page'),
    path('bank_details/', bank_details_view.BankDetailsView.as_view(), name='bank_details'),
    path('event_tickets/<int:pk>/', event_tickets_view.EventTicketsView.as_view(), name="event_tickets"),
    path('list_follower/', followers_list_view.FollowersListView.as_view(), name='list_follower'),
    path('list_subscriber/', subscriber_list_view.SubscriberListView.as_view(), name='list_subscriber'),
    path('clear_regular_members/', clear_regular_members_view.ClearRegularMembersView.as_view(), name='clear_regular_members'),
    
    #Student
    path('all_events/', all_events_view.AllEventsView.as_view(), name='all_events'),
    path('all_societies/', all_societies_view.AllSocietiesView.as_view(), name='all_societies'),
    path('society_page/<int:pk>/', society_page_view.SocietyPageView.as_view(), name='society_page'),
    path('follow_society/', follow_society_view.FollowSocietyView.as_view(), name='follow_society'),
    path('subscribe_society/', subscribe_society_view.SubscribeSocietyView.as_view(), name='subscribe_society'),
    path('for_you_page/', for_you_page_view.ForYouPageView.as_view(), name='for_you_page'),
    path('save_event/', save_event_view.SaveEventView.as_view(), name='save_event'),
    path('event_page/<int:pk>/', event_page_view.StudentEventPageView.as_view(), name='event_page'),
    path('add_to_cart/', add_to_cart_view.AddToCartView.as_view(), name='add_to_cart'),
    path('buy_membership/', buy_membership_view.BuyMembershipView.as_view(), name='buy_membership'),
    path('cart_detail/', cart_detail_view.CartDetailView.as_view(), name='cart_detail'),
    path('update_cart/', update_cart_view.UpdateCartView.as_view(), name='update_cart'), 
    path('checkout/', checkout_view.CheckoutView.as_view(), name='checkout'), 
    path('order_detail/<int:pk>', order_detail_view.OrderDetailView.as_view(), name='order_detail'),
    path('order_detail/<int:pk>/tickets/', ticket_view.TicketView.as_view(), name='tickets'),
    path('list_order_history/', order_history_list_view.ListOrderHistoryView.as_view(), name='list_order_history'),
]

if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)