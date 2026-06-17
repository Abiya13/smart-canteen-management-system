from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from AdminApp.models import Category, Food
from UserApp.models import User, ContactDb, SaveCheckout, Order, DiningBooking

def admin_loginpage(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard') if request.user.is_superuser else redirect('staff_dashboard')
    return render(request, "Admin_Login.html")


def admin_login(request):
    if request.method == "POST":
        u_name = request.POST.get("username")
        u_password = request.POST.get("password")
        user = authenticate(username=u_name, password=u_password)

        if user is not None and user.is_staff:
            login(request, user)
            request.session['username'] = u_name
            messages.success(request, f"Welcome, {u_name}! Successfully logged in.")

            # Traffic Control: Superuser goes to Analytics; Staff goes to Staff Dashboard
            if user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('staff_dashboard')
        else:
            messages.error(request, "Invalid credentials or unauthorized access.")
    return redirect('admin_loginpage')


def logout_admin(request):
    logout(request)
    request.session.flush()
    return redirect('admin_loginpage')

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('staff_dashboard')

    in_kitchen = SaveCheckout.objects.filter(status__in=['Confirmed', 'Preparing']).count()

    today = timezone.now().date()
    active_tables = DiningBooking.objects.filter(status='Confirmed', date_time__date=today).count()

    context = {
        'total_sales': SaveCheckout.objects.filter(status='Delivered').count(),
        'active_bookings': active_tables,
        'pending_orders': in_kitchen,
        'messages_count': ContactDb.objects.count(),
    }
    return render(request, 'Dashboard.html', context)

@login_required
def add_category(request):
    return render(request, "AddCategory.html")

@login_required
def save_category(request):
    if request.method == "POST":
        Category.objects.create(
            category_name=request.POST.get('category_name'),
            description=request.POST.get('description'),
            category_image=request.FILES.get('category_image')
        )
        messages.success(request, "Category added successfully!")
    return redirect('view_category')

@login_required
def view_category(request):
    categories = Category.objects.all()
    return render(request, 'ViewCategory.html', {'categories': categories})

@login_required
def edit_category(request, cat_id):
    category = get_object_or_404(Category, id=cat_id)
    return render(request, 'EditCategory.html', {'category': category})

@login_required
def update_category(request, c_id):
    if request.method == "POST":
        cat = get_object_or_404(Category, id=c_id)
        cat.category_name = request.POST.get('category_name')
        cat.description = request.POST.get('description')
        if 'category_image' in request.FILES:
            cat.category_image = request.FILES['category_image']
        cat.save()
        messages.success(request, "Category updated!")
    return redirect('view_category')

@login_required
def delete_category(request, category_id):
    get_object_or_404(Category, id=category_id).delete()
    return redirect('view_category')

@login_required
def add_food(request):
    categories = Category.objects.all()
    return render(request, "AddFood.html", {"categories": categories})

@login_required
def save_food(request):
    if request.method == "POST":
        category = get_object_or_404(Category, id=request.POST.get("category"))
        Food.objects.create(
            food_name=request.POST.get("food_name"),
            category=category,
            price=request.POST.get("price"),
            food_image=request.FILES.get("food_image"),
            availability=request.POST.get("availability"),
            description=request.POST.get("description"),
        )
        messages.success(request, "Food item saved!")
    return redirect('add_food')


@login_required
def view_food(request):

    query = request.GET.get('search')

    if query:
        foods = Food.objects.select_related("category").filter(
            food_name__icontains=query
        )
    else:
        foods = Food.objects.select_related("category").all()

    context = {
        "foods": foods,
        "query": query
    }

    return render(request, "ViewFood.html", context)


@login_required
def edit_food(request, food_id):
    food = get_object_or_404(Food, id=food_id)
    categories = Category.objects.all()
    return render(request, "EditFood.html", {"food": food, "categories": categories})


@login_required
def update_food(request, food_id):
    if request.method == "POST":
        food = get_object_or_404(Food, id=food_id)
        food.category = get_object_or_404(Category, id=request.POST.get("category"))
        food.food_name = request.POST.get("food_name")
        food.price = request.POST.get("price")
        food.availability = request.POST.get("availability")
        food.description = request.POST.get("description")
        food.prebook_only = request.POST.get('prebook_only') == 'on'

        if 'food_image' in request.FILES:
            food.food_image = request.FILES['food_image']
        food.save()
        messages.success(request, "Food item updated!")
    return redirect('view_food')


@login_required
def delete_food(request, food_id):
    get_object_or_404(Food, id=food_id).delete()
    return redirect('view_food')


@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect('user_home')

    today = timezone.now().date()

    foods = Food.objects.select_related("category").all()

    context = {
        'today': today,
        'foods': foods,
        'pending_count': SaveCheckout.objects.filter(status='Pending').count(),
        'preparing_count': SaveCheckout.objects.filter(status='Preparing').count(),
        'delivered_today': SaveCheckout.objects.filter(status='Delivered', order_date=today).count(),
    }
    return render(request, 'staff_dashboard.html', context)


@login_required
def live_orders(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_home')

    # Sorting by order_date and order_time ensures the soonest pickups are at the top
    orders = SaveCheckout.objects.filter(
        status__in=['Confirmed', 'Preparing']
    ).prefetch_related('items__food').order_by('order_date', 'order_time')

    return render(request, 'live_orders.html', {'orders': orders})

@login_required
def update_order_status(request, order_id, status):
    if request.user.is_superuser:
        messages.error(request, "Admins only have view-access for live orders.")
        return redirect('live_orders')

    order = get_object_or_404(SaveCheckout, id=order_id)
    order.status = status
    order.save()
    messages.success(request, f"Order status updated to {status}")
    return redirect('live_orders')

@login_required
def complete_order(request, order_id):
    if not request.user.is_staff:
        return redirect('user_home')

    order = get_object_or_404(SaveCheckout, id=order_id)
    order.status = "Delivered"
    order.save()
    messages.success(request, f"Token #{order.id} marked as Collected!")
    return redirect('live_orders')

@login_required
def view_bookings(request):
    bookings = DiningBooking.objects.all().order_by('date_time')
    return render(request, 'view_bookings.html', {'bookings': bookings})

@login_required
def update_booking_status(request, booking_id, status):
    booking = get_object_or_404(DiningBooking, id=booking_id)
    booking.status = status
    booking.save()
    return redirect('view_bookings')

@login_required
def manage_staff(request):
    if not request.user.is_superuser:
        return redirect('staff_dashboard')

    staff_members = User.objects.filter(is_staff=True)
    regular_users = User.objects.filter(is_staff=False, is_superuser=False)

    if request.method == "POST":
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user_to_update = get_object_or_404(User, id=user_id)

        if action == "promote":
            user_to_update.is_staff = True
            messages.success(request, f"{user_to_update.username} promoted.")
        elif action == "demote":
            user_to_update.is_staff = False
            messages.warning(request, f"{user_to_update.username} demoted.")

        user_to_update.save()
        return redirect('manage_staff')

    return render(request, 'manage_staff.html', {'staff': staff_members, 'regular_users': regular_users})


@login_required
def view_feedback(request):
    feedbacks = ContactDb.objects.all().order_by('-id')
    return render(request, 'feedback.html', {'feedbacks': feedbacks})

@login_required
def toggle_availability(request, food_id, status):
    food = get_object_or_404(Food, id=food_id)
    food.availability = status
    food.save()

    messages.success(request, f"{food.food_name} availability updated!")
    return redirect('staff_dashboard')


@login_required
def staff_reservations(request):
    if not request.user.is_staff:
        return redirect('user_home')

    bookings = DiningBooking.objects.all().order_by('date_time')

    return render(request, 'staff_reservations.html', {
        'bookings': bookings
    })