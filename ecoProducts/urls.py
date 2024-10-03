"""
URL configuration for ecoProducts project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin

from django.urls import path

from mystore import views

from django.conf import settings

from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    path('register/',views.SignUpView.as_view(),name="register"),

    path('',views.SignInView.as_view(),name="signin"),

    path('profile_edit/<int:pk>/change/',views.UserProfileView.as_view(),name="profile-edit"),

    path('productlist/',views.ProductListView.as_view(),name="product-list"),

    path('product_detail/<int:pk>/',views.ProductDetailView.as_view(),name="product-detail"),

    path('product/<int:pk>/cart/add/',views.ProductAddCartView.as_view(),name="cart-add"),

    path('products/cartitems',views.MyCartView.as_view(),name="cart-items"),

    path('product/<int:pk>/remove',views.MyCartItemDeleteView.as_view(),name="cartitem-delete"),

    path('product/delivery/',views.AddressView.as_view(),name="delivery-address"),

    path('checkout/',views.CheckOutView.as_view(),name="checkout"),

    path('payment/verify/',views.PaymentVerificationView.as_view(),name="payment-verify"),

    path('payment_method/',views.PaymentVerificationView.as_view(),name="payment_method"),

    path('order/summary',views.MyPurchaseView.as_view(),name="order-summary"),

    path('project/<int:pk>/review/add/',views.ReviewCreateView.as_view(),name="review-add"),

    path('signout',views.SignOutView.as_view(),name="signout"),

    path('product/<int:pk>/dropdown/',views.ProductDropDownView.as_view(),name="dropdown"),



    

    

    

    



    


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
