"""
Baby Hug – Store Models
Mirrors the database design from the SRS/System Design document.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# ─────────────────────────────────────────────────────────────────────────────
# PROFILE (extends the built-in User)
# ─────────────────────────────────────────────────────────────────────────────
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile({self.user.username})"


# ─────────────────────────────────────────────────────────────────────────────
# ADDRESS
# ─────────────────────────────────────────────────────────────────────────────
class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [('Home', 'Home'), ('Work', 'Work'), ('Other', 'Other')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    house_no = models.CharField(max_length=50)
    street = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    address_type = models.CharField(max_length=30, choices=ADDRESS_TYPE_CHOICES, default='Home')
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.full_name} – {self.city}, {self.state}"


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY
# ─────────────────────────────────────────────────────────────────────────────
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT
# ─────────────────────────────────────────────────────────────────────────────
class Product(models.Model):
    AGE_GROUP_CHOICES = [
        ('0-3M',  '0–3 Months'),
        ('3-6M',  '3–6 Months'),
        ('6-12M', '6–12 Months'),
        ('1-2Y',  '1–2 Years'),
        ('2-4Y',  '2–4 Years'),
    ]

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    size = models.CharField(max_length=50, blank=True)
    colour = models.CharField(max_length=50, blank=True)
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES, blank=True)
    image = models.ImageField(upload_to='products/')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    @property
    def avg_rating(self):
        reviews = self.reviews.filter(status='Approved')
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    @property
    def review_count(self):
        return self.reviews.filter(status='Approved').count()


class ProductImage(models.Model):
    """Extra gallery images for a product."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"


# ─────────────────────────────────────────────────────────────────────────────
# CART
# ─────────────────────────────────────────────────────────────────────────────
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart({self.user.username})"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return self.items.count()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity


# ─────────────────────────────────────────────────────────────────────────────
# WISHLIST
# ─────────────────────────────────────────────────────────────────────────────
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} – {self.product.name}"


# ─────────────────────────────────────────────────────────────────────────────
# ORDER
# ─────────────────────────────────────────────────────────────────────────────
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending',    'Pending'),
        ('Confirmed',  'Confirmed'),
        ('Processing', 'Processing'),
        ('Shipped',    'Shipped'),
        ('Delivered',  'Delivered'),
        ('Cancelled',  'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    order_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order#{self.pk} – {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at time of order
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"


# ─────────────────────────────────────────────────────────────────────────────
# PAYMENT
# ─────────────────────────────────────────────────────────────────────────────
class Payment(models.Model):
    METHOD_CHOICES = [
        ('UPI',        'UPI'),
        ('Card',       'Credit / Debit Card'),
        ('NetBanking', 'Net Banking'),
        ('COD',        'Cash on Delivery'),
    ]
    STATUS_CHOICES = [
        ('Pending',    'Pending'),
        ('Successful', 'Successful'),
        ('Failed',     'Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=30, choices=METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Payment#{self.pk} – {self.payment_status}"


# ─────────────────────────────────────────────────────────────────────────────
# REVIEW
# ─────────────────────────────────────────────────────────────────────────────
class Review(models.Model):
    STATUS_CHOICES = [('Approved', 'Approved'), ('Hidden', 'Hidden'), ('Pending', 'Pending')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-review_date']

    def __str__(self):
        return f"{self.user.username} → {self.product.name} ({self.rating}★)"


# ─────────────────────────────────────────────────────────────────────────────
# FEEDBACK
# ─────────────────────────────────────────────────────────────────────────────
class Feedback(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Responded', 'Responded')]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    response = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Feedback: {self.subject} from {self.email}"
