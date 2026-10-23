from django.contrib import admin
from .models import (
    Profile, Address, Category, Product, ProductImage,
    Cart, CartItem, Wishlist, Order, OrderItem, Payment, Review, Feedback
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)
    search_fields = ('name',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'is_featured')
    list_filter = ('category', 'is_active', 'is_featured', 'age_group')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'is_featured', 'stock')
    inlines = [ProductImageInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_blocked', 'created_at')
    list_filter = ('is_blocked',)
    search_fields = ('user__username', 'user__email')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'state', 'pincode', 'address_type')
    search_fields = ('user__username', 'city', 'pincode')


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'total', 'updated_at')
    inlines = [CartItemInline]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    search_fields = ('user__username', 'product__name')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'order_date')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email')
    list_editable = ('status',)
    inlines = [OrderItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'payment_method', 'amount', 'payment_status', 'payment_date')
    list_filter = ('payment_status', 'payment_method')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'status', 'review_date')
    list_filter = ('status', 'rating')
    list_editable = ('status',)
    search_fields = ('user__username', 'product__name')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'submitted_at')
    list_filter = ('status',)
    search_fields = ('name', 'email', 'subject')
