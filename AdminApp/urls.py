from django.urls import path
from AdminApp import views

urlpatterns = [

    path('Dashboard/', views.admin_dashboard, name="admin_dashboard"),
    path('', views.admin_loginpage, name="admin_loginpage"),
    path('AdminLogin/', views.admin_login, name="admin_login"),
    path('AdminLogout/', views.logout_admin, name="logout_admin"),

    path('AddCategory/', views.add_category, name="add_category"),
    path('SaveCategory/', views.save_category, name="save_category"),
    path('ViewCategory/', views.view_category, name='view_category'),
    path('EditCategory/<int:cat_id>/', views.edit_category, name='edit_category'),
    path('UpdateCategory/<int:c_id>/', views.update_category, name='update_category'),
    path('DeleteCategory/<int:category_id>/', views.delete_category, name='delete_category'),

    path('AddFood/', views.add_food, name="add_food"),
    path('SaveFood/', views.save_food, name="save_food"),
    path('ViewFood/', views.view_food, name="view_food"),
    path('EditFood/<int:food_id>/', views.edit_food, name="edit_food"),
    path('UpdateFood/<int:food_id>/', views.update_food, name="update_food"),
    path('DeleteFood/<int:food_id>/', views.delete_food, name="delete_food"),

    path('LiveOrders/', views.live_orders, name='live_orders'),
    path('UpdateOrderStatus/<int:order_id>/<str:status>/', views.update_order_status, name='update_order_status'),
    path('complete-order/<int:order_id>/', views.complete_order, name='complete_order'),

    path('ViewBookings/', views.view_bookings, name='view_bookings'),
    path('UpdateBooking/<int:booking_id>/<str:status>/', views.update_booking_status, name='update_booking_status'),

    path('ManageStaff/', views.manage_staff, name='manage_staff'),
    path('feedback/', views.view_feedback, name='view_feedback'),

    path('staff-home/', views.staff_dashboard, name='staff_dashboard'),
    path('toggle-availability/<int:food_id>/<str:status>/', views.toggle_availability, name='toggle_availability'),
    path('staff/reservations/', views.staff_reservations, name='staff_reservations'),
]