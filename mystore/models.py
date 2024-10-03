from django.db import models

from django.contrib.auth.models import User

from django.db.models import Sum,Avg


# Create your models here.


class UserProfile(models.Model):

    bio=models.CharField(max_length=200)

    pro_pic=models.FileField(upload_to='pofile_pictures',default='/pofile_pictures/default.png')

    user_object=models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)

    def __str__(self) :

        return self.user_object.username
    
class Brand(models.Model):

    brand_name=models.CharField(max_length=200,unique=True)

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)

    def __str__(self):

        return self.brand_name
    
class Product(models.Model):

    product_name=models.CharField(max_length=200)

    description=models.TextField(max_length=300)

    brand_object=models.ForeignKey(Brand,on_delete=models.CASCADE)

    owner=models.ForeignKey(User,on_delete=models.CASCADE,related_name="products")

    product_pic=models.ImageField(upload_to="products",null=True)

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)


    def __str__(self):
        return self.product_name
    
# class ProductQuantity(models.Model):

#     qty_object=models.CharField(max_length=200,null=True)

#     created_date=models.DateTimeField(auto_now_add=True)

#     updated_date=models.DateTimeField(auto_now=True)

#     is_active=models.BooleanField(default=True)


    
class ProductVarient(models.Model):

    product_object=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="productvarients")

    product_quantity=models.CharField(max_length=200)

    price=models.PositiveIntegerField()

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)

    @property
    def buyers(self):     #this custom methode for take the count of product buyers 

        return OrderSummary.objects.filter(is_paid=True,productvarient_object=self).count()
    
    @property
    def review_count(self):  #this custom methode for take the count of product reviews

       return self.product_reviews.all().count()
    @property
    def average_rating(self):  #this custom methode for take the avereage count of product reviews

        return self.product_reviews.all().values('rating').aggregate(avg=Avg('rating')).get('avg',0)

    

class Cart(models.Model):

    owner=models.OneToOneField(User,on_delete=models.CASCADE,related_name="cart")

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)

    @property
    def cart_total(self):

        return self.cart_items.filter(is_order_placed=False).values("productvarient_object__price").aggregate(total=Sum("productvarient_object__price")).get("total")


class CartItems(models.Model):

    Cart_object=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="cart_items")

    productvarient_object=models.ForeignKey(ProductVarient,on_delete=models.CASCADE,null=True)

    is_order_placed=models.BooleanField(default=False)

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)


class OrderSummary(models.Model):

    user_object=models.ForeignKey(User,on_delete=models.CASCADE,related_name='orders')

    productvarient_object=models.ManyToManyField(ProductVarient)

    name=models.CharField(max_length=200)

    phone=models.CharField(max_length=50)

    email=models.EmailField(max_length=50)

    pin=models.CharField(max_length=50)

    delivery_address=models.TextField()

    order_id=models.CharField(max_length=200)

    payment_option=(
        ("online_payment","online_payment"),
        ("cash_on_delivery","cash_on_delivery")
    )

    payment_methode=models.CharField(max_length=200,choices=payment_option,null=True)

    is_paid=models.BooleanField(default=False)

    total=models.FloatField(null=True)

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)


#this is used for creating default profile
from django.db.models.signals import post_save

def create_profile(sender,instance,created,*args,**kwargs):

    if created:

        UserProfile.objects.create(user_object=instance)

post_save.connect(sender=User,receiver=create_profile)


#this is used for creating default cart
def create_cart(sender,instance,created,*args,**kwargs):

    if created:

        Cart.objects.create(owner=instance)

post_save.connect(sender=User,receiver=create_cart)

from django.core.validators import MinValueValidator,MaxValueValidator

class Reviews(models.Model):

    product_object=models.ForeignKey(ProductVarient,on_delete=models.CASCADE,related_name="product_reviews")

    user_object=models.ForeignKey(User,on_delete=models.CASCADE)

    comment=models.TextField()

    rating=models.FloatField(default=1,validators=[MinValueValidator(1),MaxValueValidator(5)])
 
    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)




