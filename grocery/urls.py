from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.product_search, name='product_search'),
    path('category/<int:category_id>/', views.category_view, name='category_products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('submit-comment/<int:product_id>/', views.submit_comment, name='submit_comment'),
    path('cart/', views.view_cart, name='view_cart'),
    path('update-cart/<int:product_id>/', views.update_cart_quantity, name="update_cart_quantity"),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-success/<int:order_id>/', views.order_success, name="order_success"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
