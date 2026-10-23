"""
Baby Hug – Store Views
"""

import uuid
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import (
    Profile, Address, Category, Product, ProductImage,
    Cart, CartItem, Wishlist, Order, OrderItem, Payment, Review, Feedback
)


# ─────────────────────────────────────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────────────────────────────────────
AGE_CHOICES = [
    ('0-3M',  '0–3 Months'),
    ('3-6M',  '3–6 Months'),
    ('6-12M', '6–12 Months'),
    ('1-2Y',  '1–2 Years'),
    ('2-4Y',  '2–4 Years'),
]


def home(request):
    categories = Category.objects.filter(is_active=True)[:6]
    featured = Product.objects.filter(is_active=True, is_featured=True)[:8]
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    bestsellers = Product.objects.filter(is_active=True).order_by('-id')[:4]
    return render(request, 'store/home.html', {
        'categories': categories,
        'featured_products': featured,
        'new_arrivals': new_arrivals,
        'bestsellers': bestsellers,
        'age_groups': AGE_CHOICES,
    })


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT LISTING
# ─────────────────────────────────────────────────────────────────────────────
def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)

    # Search
    q = request.GET.get('q', '')
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))

    # Category filter
    cat_slug = request.GET.get('category', '')
    selected_category = None
    if cat_slug:
        selected_category = get_object_or_404(Category, slug=cat_slug, is_active=True)
        products = products.filter(category=selected_category)

    # Age group filter
    age = request.GET.get('age', '')
    if age:
        products = products.filter(age_group=age)

    # Price filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Sort
    sort = request.GET.get('sort', 'popular')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-is_featured', '-created_at')

    return render(request, 'store/product_list.html', {
        'age_choices': AGE_CHOICES,
        'age_choices_json': json.dumps(dict(AGE_CHOICES)),
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'q': q,
        'age': age,
        'sort': sort,
    })


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT DETAIL
# ─────────────────────────────────────────────────────────────────────────────
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.filter(status='Approved').select_related('user')
    related = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk)[:4]

    user_review = None
    in_wishlist = False
    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user, product=product).first()
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        rating = int(request.POST.get('rating', 5))
        text = request.POST.get('review_text', '').strip()
        if text:
            Review.objects.update_or_create(
                user=request.user, product=product,
                defaults={'rating': rating, 'review_text': text, 'status': 'Pending'}
            )
            messages.success(request, 'Your review has been submitted for approval.')
            return redirect('product_detail', slug=slug)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'related': related,
        'user_review': user_review,
        'in_wishlist': in_wishlist,
    })


# ─────────────────────────────────────────────────────────────────────────────
# CART
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    return render(request, 'store/cart.html', {'cart': cart, 'items': items})


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    messages.success(request, f'"{product.name}" added to cart.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.item_count})
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


@login_required
@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    qty = int(request.POST.get('quantity', 1))
    if qty < 1:
        item.delete()
    else:
        item.quantity = qty
        item.save()
    return redirect('cart')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


# ─────────────────────────────────────────────────────────────────────────────
# WISHLIST
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'items': items})


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.delete()
        msg = 'Removed from wishlist.'
    else:
        msg = f'"{product.name}" added to wishlist.'
    messages.success(request, msg)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'in_wishlist': created})
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))


@login_required
@require_POST
def move_to_cart(request, wishlist_item_id):
    wish = get_object_or_404(Wishlist, pk=wishlist_item_id, user=request.user)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=wish.product)
    if not created:
        item.quantity += 1
        item.save()
    wish.delete()
    messages.success(request, f'"{wish.product.name}" moved to cart.')
    return redirect('wishlist')


# ─────────────────────────────────────────────────────────────────────────────
# CHECKOUT & ORDER
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.select_related('product').all()
    if not items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method', 'COD')

        # Use existing or create new address
        if address_id:
            address = get_object_or_404(Address, pk=address_id, user=request.user)
        else:
            address = Address.objects.create(
                user=request.user,
                full_name=request.POST.get('full_name', request.user.get_full_name()),
                phone=request.POST.get('phone', ''),
                house_no=request.POST.get('house_no', ''),
                street=request.POST.get('street', ''),
                city=request.POST.get('city', ''),
                state=request.POST.get('state', ''),
                pincode=request.POST.get('pincode', ''),
                address_type=request.POST.get('address_type', 'Home'),
            )

        with transaction.atomic():
            # Verify stock
            for item in items:
                if item.product.stock < item.quantity:
                    messages.error(request, f'Insufficient stock for "{item.product.name}".')
                    return redirect('cart')

            # Create order
            order = Order.objects.create(
                user=request.user,
                address=address,
                total_amount=cart.total,
                status='Pending',
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                    subtotal=item.subtotal,
                )
                # Deduct stock
                item.product.stock -= item.quantity
                item.product.save(update_fields=['stock'])

            # Create payment record
            Payment.objects.create(
                order=order,
                payment_method=payment_method,
                transaction_id=str(uuid.uuid4()) if payment_method != 'COD' else None,
                amount=cart.total,
                payment_status='Successful' if payment_method != 'COD' else 'Pending',
            )

            # Clear cart
            cart.items.all().delete()

        messages.success(request, f'Order #{order.pk} placed successfully! 🎉')
        return redirect('order_confirmation', order_id=order.pk)

    return render(request, 'store/checkout.html', {
        'cart': cart,
        'items': items,
        'addresses': addresses,
    })


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'store/order_confirmation.html', {'order': order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product', 'payment')
    return render(request, 'store/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    order_statuses = [
        ('Pending',    'Pending',    'hourglass_empty'),
        ('Confirmed',  'Confirmed',  'task_alt'),
        ('Processing', 'Processing', 'inventory'),
        ('Shipped',    'Shipped',    'local_shipping'),
        ('Delivered',  'Delivered',  'check_circle'),
    ]
    status_order = [s[0] for s in order_statuses]
    status_index = status_order.index(order.status) if order.status in status_order else 0
    return render(request, 'store/order_detail.html', {
        'order': order,
        'order_statuses': order_statuses,
        'status_index': status_index,
    })


@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if order.status in ('Pending', 'Confirmed'):
        with transaction.atomic():
            order.status = 'Cancelled'
            order.save()
            # Restore stock
            for item in order.items.all():
                item.product.stock += item.quantity
                item.product.save(update_fields=['stock'])
        messages.success(request, f'Order #{order.pk} has been cancelled.')
    else:
        messages.error(request, 'This order cannot be cancelled at its current stage.')
    return redirect('my_orders')


# ─────────────────────────────────────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', request.user.email)
            request.user.save()
            profile_obj.phone = request.POST.get('phone', '')
            profile_obj.save()
            messages.success(request, 'Profile updated successfully.')

        elif action == 'change_password':
            current = request.POST.get('current_password')
            new_pw = request.POST.get('new_password')
            confirm = request.POST.get('confirm_password')
            if not request.user.check_password(current):
                messages.error(request, 'Current password is incorrect.')
            elif new_pw != confirm:
                messages.error(request, 'New passwords do not match.')
            else:
                request.user.set_password(new_pw)
                request.user.save()
                messages.success(request, 'Password changed. Please log in again.')
                return redirect('login')

        elif action == 'add_address':
            Address.objects.create(
                user=request.user,
                full_name=request.POST.get('full_name', ''),
                phone=request.POST.get('phone', ''),
                house_no=request.POST.get('house_no', ''),
                street=request.POST.get('street', ''),
                city=request.POST.get('city', ''),
                state=request.POST.get('state', ''),
                pincode=request.POST.get('pincode', ''),
                address_type=request.POST.get('address_type', 'Home'),
            )
            messages.success(request, 'Address added.')

        return redirect('profile')

    return render(request, 'store/profile.html', {
        'profile': profile_obj,
        'addresses': addresses,
    })


# ─────────────────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
        elif len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            Profile.objects.create(user=user, phone=phone)
            login(request, user)
            messages.success(request, f'Welcome to Baby Hug, {first_name}! 🎉')
            return redirect('home')

    return render(request, 'store/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'home'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'store/login.html', {'next': request.GET.get('next', '')})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


# ─────────────────────────────────────────────────────────────────────────────
# FEEDBACK / CONTACT
# ─────────────────────────────────────────────────────────────────────────────
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and subject and message:
            Feedback.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name, email=email, subject=subject, message=message,
            )
            messages.success(request, "Thank you for your message! We'll get back to you soon.")
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all fields.')

    return render(request, 'store/contact.html')
