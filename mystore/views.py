from django.shortcuts import render,redirect,get_object_or_404

from django.views.generic import View,TemplateView,UpdateView,DetailView,ListView,FormView

from mystore.forms import RegistrationForm,LoginForm,UserProfileFrom,DeliveryAdderssForm,ReviewForm

from django.contrib.auth import authenticate,login,logout

from mystore.models import UserProfile,ProductVarient,Product,CartItems,OrderSummary,Reviews

from django.db.models import Sum

from django.urls import reverse_lazy

from django.views.decorators.csrf import csrf_exempt

from django.utils.decorators import method_decorator

from mystore.decorators import signin_requierd




import razorpay

from django.db import IntegrityError


KEY_SECRET="Oz5j9JeIpOofpt6KYavwBipK"

KEY_ID="rzp_test_ekHyATIcPyEQir"

class SignUpView(View):

    def get(self,request,*args,**kwargs):

        form_instance=RegistrationForm()

        return render(request,"store/registration.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance=RegistrationForm(request.POST)

        if form_instance.is_valid():

            form_instance.save()

            return redirect('signin')
        
        else:

            return render(request,"store/registration.html",{"form":form_instance})
        
class SignInView(View):

    def get(self,request,*args,**kwargs):

        form_instance=LoginForm()

        return render(request,"store/login.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance=LoginForm(request.POST)

        if form_instance.is_valid():
             
             data=form_instance.cleaned_data

             user_obj=authenticate(request,**form_instance.cleaned_data)
     
             if user_obj:
     
                 login(request,user_obj)

                 return redirect("intro")
             
             else:
                 
                 return render(request,"store/login.html",{"form":form_instance})


class UserProfileView(UpdateView):

    model=UserProfile

    form_class=UserProfileFrom

    template_name="store/profile_edit.html"

    success_url=reverse_lazy("product-list")  #this used as as redirect
    

class ProductListView(View):

    def get(self,request,*args,**kwargs):

        qs=Product.objects.all()

        return render(request,"store/productlist.html",{"products":qs})
    
    def post(self, request, *args, **kwargs):

        selected_type_id = request.POST.get('name')
    
        names = Product.objects.all()
    
        products = Product.objects.filter(id=selected_type_id)
    
        return render(request, "store/productlist.html", {"names": names, "products": products})


  
class ProductDetailView(DetailView):

    model=ProductVarient

    template_name="store/product_detail.html"

    context_object_name="product"

@method_decorator(signin_requierd,name="dispatch")
class ProductAddCartView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        product_obj=ProductVarient.objects.get(id=id)

        CartItems.objects.create(

                                 Cart_object=request.user.cart,  #here products add to cart items
                                 
                                 productvarient_object=product_obj

        )

        return redirect('cart-items')
    
@method_decorator(signin_requierd,name="dispatch")
class MyCartView(View):

    def get(self,request,*args,**kwargs):

        qs=request.user.cart.cart_items.filter(is_order_placed=False)       
                                                                                     #here take the sum of cart aggregate is used here for take both the sum of django and python
        total=request.user.cart.cart_items.filter(is_order_placed=False).values("productvarient_object__price").aggregate(total=Sum("productvarient_object__price")).get("total")

     

        return render(request,"store/mycartitems.html",{"cartitem":qs,"total":total})
      
@method_decorator(signin_requierd,name="dispatch")
class MyCartItemDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        CartItems.objects.get(id=id).delete()

        return redirect("cart-items")
    
@method_decorator(signin_requierd,name="dispatch")
class AddressView(View):

    def get(self,request,*args,**kwargs):
        
        form_instance = DeliveryAdderssForm()
        
        return render(request,"store/deliveryaddress.html",{"form":form_instance})

    def post(self,request,*args,**kwargs):
        
        cart_items = request.user.cart.cart_items.filter(is_order_placed = False)

        form_instance = DeliveryAdderssForm(request.POST)

        
        if form_instance.is_valid():

            data = form_instance.cleaned_data

            order_summary_obj = OrderSummary.objects.create(
            user_object = request.user,
            total = request.user.cart.cart_total,
            **data
        
        )
          
        for ci in cart_items:

            order_summary_obj.productvarient_object.add(ci.productvarient_object)

            order_summary_obj.save()

        if order_summary_obj.payment_methode =='cash_on_delivery':

            for ci in cart_items:

                ci.is_order_placed = True

                ci.save()
                
            return redirect('order-summary')
        else:
            
            return redirect('checkout')
    



@method_decorator(signin_requierd,name="dispatch")
class CheckOutView(View):

    def get(self, request, *args, **kwargs):

        client = razorpay.Client(auth=(KEY_ID,KEY_SECRET)) # Create a Razorpay client instance with your API key and secret

        amount=(request.user.cart.cart_total) * 100 # Calculate the amount to be paid in paise

        data={"amount":amount,"currency":"INR","receipt":"order_rcptid_11"} # Create a payment order data dictionary

        payment=client.order.create(data=data) # Create a payment order using the Razorpay client


        OrderSummary.objects.filter(          # Create an order summary object

                           user_object=request.user,
                           payment_methode='online_payment',
                           order_id__isnull=True
                           ).update(order_id=payment.get('id'))
               
        cart_items=request.user.cart.cart_items.filter(is_order_placed=False)

        # Associate the mobile variant objects with the order summary
        for ci in cart_items:

            ci.is_order_placed =True

            ci.save()

        # Create a context dictionary to pass to the template
        context={
            'key':KEY_ID,
            'amount':data.get('amount'),
            'currency':data.get('currency'),
            'order_id':payment.get('id'),
        }

        return render(request,'store/payment.html',context)
    


@method_decorator(csrf_exempt,name="dispatch")   
class PaymentVerificationView(View):

    def post(self, request, *args, **kwargs):

        print(request.POST)

        client = razorpay.Client(auth=(KEY_ID,KEY_SECRET)) # Create a Razorpay client instance with authentication credentials

        order_summary_object=OrderSummary.objects.get(order_id=request.POST.get('razorpay_order_id')) # Retrieve the OrderSummary object from the database using the order_id

        login(request,order_summary_object.user_object) # Log in the user associated with the order summary object

        try:

            client.utility.verify_payment_signature(request.POST) # Verify the payment signature using the Razorpay client

            print('Payment Successfully verified')

            # Update the OrderSummary object to mark the payment as paid
            order_id = request.POST.get('razorpay_order_id')

            OrderSummary.objects.filter(order_id=order_id).update(is_paid=True)

            # Update the cart items to mark them as ordered
            cart_items=request.user.cart.cart_items.filter(is_order_placed=False)
            
            for m in cart_items:
                
                m.is_order_placed=True
                
                m.save()
            
        except:

            print('Payment Failed') # Print an error message if the verification fails

        return redirect('order-summary')

        
@method_decorator(signin_requierd,name="dispatch")
class MyPurchaseView(View):

    model=OrderSummary

    context_object_name="orders"

    def get(self,request,*args,**kwargs):

        qs=OrderSummary.objects.filter(user_object=request.user).order_by("-created_date") #here take the products from ordersummary when is_order paid is true

        return render(request,"store/order_summary.html",{"orders":qs}) 
    
#localhost:8000/projects/<int:pk>/review/add/
@method_decorator(signin_requierd,name="dispatch")
class ReviewCreateView(FormView):

    template_name="store/review.html"

    form_class=ReviewForm

    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        product_obj=ProductVarient.objects.get(id=id)

        form_instance=ReviewForm(request.POST)

        if form_instance.is_valid():

            form_instance.instance.user_object=(request.user)    #here adding user in form_instance

            form_instance.instance.product_object=product_obj

            form_instance.save()

            return redirect("product-list")
        
        else:

            return render(request,self.template_name,{"form":form_instance})
        

 
class SignOutView(View):

    def get(self,request,*args,**kwargs):

        logout(request)

        return redirect("signin")
    
class ProductDropDownView(View):

        def get(self,request,*args,**kwargs):

           category=request.GET.get("category")

           qs=Product.objects.filter(category=category)

           return render(request,"store/product_drop_down.html",{"products":qs})
        
class IntroductionView(TemplateView):

    template_name="store/intro.html"


class ProductCategoryView(View):

    def get(self,request,*args,**kwargs):

        qs=Product.objects.all()

        return render(request,"store/base.html",{"name":qs})









           




    

    





    
    


    


    


    












   
    
   




        



        
    



             


                 



