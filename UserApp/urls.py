from django.urls import path
from UserApp import views

urlpatterns = [

    path('Home/', views.user_home, name='user_home'),
    path('menu/', views.menu, name='menu'),
    path('SingleFood/<int:food_id>/', views.single_food, name='single_food'),

    path('signin/signup/', views.signin_signup, name='signin_signup'),
    path('save_registration/', views.save_registration, name='save_registration'),
    path('userlogin/', views.user_login, name='user_login'),
    path('userlogout/', views.user_logout, name='user_logout'),

    path('About/', views.about_page, name="about_page"),
    path('Contact/', views.contact_page, name="contact_page"),
    path('SaveContact/', views.save_contact, name="save_contact"),

    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('increase/<int:cart_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:cart_id>/', views.decrease_quantity, name='decrease_quantity'),

    path('checkout/', views.checkout, name='checkout'),
    path('save_checkout_data/', views.save_checkout_data, name='save_checkout_data'),
    path('payment_page/', views.payment_page, name='payment_page'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('book-table/', views.book_table, name='book_table'),
    path('buy-now/<int:food_id>/', views.buy_now, name='buy_now'),
    path('order-success/', views.order_success, name='order_success'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment/', views.payment_page, name='payment_page'),
    path('user-cancel-booking/<int:booking_id>/', views.user_cancel_booking, name='user_cancel_booking'),
]