from django.shortcuts import render, redirect, get_object_or_404
from AdminApp.models import *
from UserApp.models import *
from django.contrib import messages
from django.utils.timezone import now
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout
from decimal import Decimal
import razorpay
from django.utils import timezone
from datetime import timedelta

def payment_page(request):
    return render(request, 'payment_page.html')

def user_home(request):
    categories = Category.objects.all()
    foods = Food.objects.filter(availability="Available").order_by('-id')[:6]
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()

    return render(request, 'Home.html', {
        'categories': categories,
        'foods': foods,
        'cart_count': cart_count,
    })


def menu(request):
    categories = Category.objects.all()
    query = request.GET.get('search')

    if query:
        foods = Food.objects.filter(food_name__icontains=query, availability='Available')
    else:
        foods = Food.objects.filter(availability='Available')

    context = {
        'categories': categories,
        'foods': foods,
        'query': query,
    }

    if request.user.is_authenticated:
        context['cart_count'] = Cart.objects.filter(user=request.user).count()

    return render(request, 'menu.html', context)


def single_food(request, food_id):
    food = get_object_or_404(Food, id=food_id)
    return render(request, 'single_food.html', {'food': food})


User = get_user_model()

def signin_signup(request):
    return render(request, "signin_signup.html")

def save_registration(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        name = request.POST.get('name')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signin_signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('signin_signup')

        User.objects.create_user(username=username, email=email, name=name, password=password)
        messages.success(request, "Registration successful. Please login.")
        return redirect('signin_signup')

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('user_home')
        messages.error(request, "Invalid username or password")
        return redirect('signin_signup')

@login_required
def user_logout(request):
    logout(request)
    return redirect('user_home')

@login_required
def add_to_cart(request, food_id):
    food = get_object_or_404(Food, id=food_id)
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        food=food,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('menu')


@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    order_items = Order.objects.filter(user=request.user, checkout__status='Pending')

    total_cart = sum(Decimal(item.food.price) * item.quantity for item in cart_items)

    grand_total = total_cart
    cart_count = cart_items.count()

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'order_items': order_items,
        'grand_total': grand_total,
        'cart_count': cart_count
    })

@login_required
def save_checkout_data(request):
    if request.method == "POST":
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty!")
            return redirect('view_cart')

        user_name = request.POST.get('username')
        user_email = request.POST.get('email')
        o_time = request.POST.get('order_time')
        o_total = request.POST.get('total_amount', 0)

        checkout_record = SaveCheckout.objects.create(
            user=request.user,
            username=user_name,
            email=user_email,
            order_type="Instant",
            order_date=date.today(),
            order_time=o_time,
            total_amount=o_total,
            status="Pending"  
        )

        for item in cart_items:
            Order.objects.create(
                checkout=checkout_record,
                user=request.user,
                food=item.food,
                quantity=item.quantity,
                total_price=item.total_price
            )

        request.session['order_id'] = checkout_record.id
        return redirect('payment_page')

    return redirect('menu')


@login_required
def payment_success(request):
    order_id = request.session.get('order_id')
    if order_id:
        checkout_record = SaveCheckout.objects.filter(id=order_id).first()
        if checkout_record:
            checkout_record.status = "Confirmed"
            checkout_record.save()

    Cart.objects.filter(user=request.user).delete()

    if 'order_id' in request.session:
        del request.session['order_id']

    return redirect('order_success')


@login_required
def increase_quantity(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('view_cart')


@login_required
def decrease_quantity(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('view_cart')


@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(Decimal(i.food.price) * i.quantity for i in cart_items)

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total": total,
        "user_name": request.user.username,
        "user_email": request.user.email,
        "today": now().date()
    })

def about_page(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
    return render(request, "About.html", {'cart_count': cart_count})

def contact_page(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
    return render(request, "Contact.html", {'cart_count': cart_count})

def save_contact(request):
    if request.method == "POST":
        ContactDb.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            subject=request.POST.get("subject"),
            message=request.POST.get("message")
        )
        messages.success(request, "Message sent successfully")
        return redirect('contact_page')

@login_required
def payment_page(request):
    customer = SaveCheckout.objects.filter(user=request.user).order_by('-id').first()

    if not customer:
        return redirect('user_home')
    
    amount_in_paise = int(customer.total_amount * 100)
    client = razorpay.Client(auth=('rzp_test_0ib0jPwwZ7I1lT', 'VjHNO5zKeKxz8PYe7VnzwxMR'))

    data = {
        "amount": amount_in_paise,
        "currency": "INR",
        "receipt": f"receipt_{customer.id}"
    }
    razorpay_order = client.order.create(data=data)

    context = {
        'customer': customer,
        'amount': amount_in_paise,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_merchant_key': 'rzp_test_0ib0jPwwZ7I1lT',  # Your Key ID
        'currency': 'INR',
    }

    return render(request, "payment_page.html", context)


@login_required
def my_orders(request):
    checkouts = SaveCheckout.objects.filter(user=request.user).order_by('-created_at')
    bookings = DiningBooking.objects.filter(user=request.user).order_by('-date_time')
    cart_count = Cart.objects.filter(user=request.user).count()

    return render(request, "my_orders.html", {
        'checkouts': checkouts,
        'bookings': bookings,
        'cart_count': cart_count,
        'now': timezone.now()
    })

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(SaveCheckout, id=order_id, user=request.user)

    now = timezone.now()
    if now <= order.created_at + timedelta(minutes=30):
        order.status = "Cancelled"
        order.save()
        messages.success(request, f"Order #{order.id} has been cancelled successfully.Your cash will be refunded within 24 hours.")
    else:
        messages.error(request, "Sorry, orders cannot be cancelled after 30 minutes.")

    return redirect('my_orders')

def book_table(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        dt_time = request.POST.get('datetime')
        p_count = request.POST.get('people')
        table_no = request.POST.get('table_number')
        request_msg = request.POST.get('special_request')

        is_booked = DiningBooking.objects.filter(
            table_number=table_no,
            date_time=dt_time
        ).exists()

        if is_booked:
            messages.error(request,
                           f"Table {table_no} is already booked for this time. Please pick another table or time.")
            return redirect("user_home")

        DiningBooking.objects.create(
            user=request.user,
            name=name,
            email=email,
            date_time=dt_time,
            table_number=table_no,
            people=p_count,
            special_request=request_msg
        )

        messages.success(request, f"Table {table_no} has been reserved for you!")

    return redirect("user_home")


@login_required
def buy_now(request, food_id):
    food = get_object_or_404(Food, id=food_id)

    Cart.objects.filter(user=request.user).delete()

    Cart.objects.create(
        user=request.user,
        food=food,
        quantity=1
    )

    return redirect('checkout')


@login_required
def order_success(request):
    checkout = SaveCheckout.objects.filter(user=request.user, status="Confirmed").order_by('-id').first()

    if not checkout:
        messages.error(request, "No recent confirmed orders found.")
        return redirect('menu')

    order_items = Order.objects.filter(checkout=checkout)

    return render(request, 'order_success.html', {
        'checkout': checkout,
        'order_items': order_items
    })


@login_required
def user_cancel_booking(request, booking_id):
    booking = get_object_or_404(DiningBooking, id=booking_id, user=request.user)

    booking.status = "Cancelled"
    booking.save()

    messages.success(request, "Your table reservation has been cancelled.")
    return redirect('my_orders')