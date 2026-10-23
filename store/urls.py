from django.urls import path
from . import views

urlpatterns = [
    # ── Core pages ──────────────────────────────────────────────────────────
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('contact/', views.contact, name='contact'),

    # ── Auth ────────────────────────────────────────────────────────────────
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ── Cart ────────────────────────────────────────────────────────────────
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # ── Wishlist ─────────────────────────────────────────────────────────────
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/move/<int:wishlist_item_id>/', views.move_to_cart, name='move_to_cart'),

    # ── Orders ──────────────────────────────────────────────────────────────
    path('checkout/', views.checkout, name='checkout'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),

    # ── Profile ──────────────────────────────────────────────────────────────
    path('profile/', views.profile, name='profile'),
]
