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

                 return redirect("product-list")
             
             else:
                 
                 return render(request,"store/login.html",{"form":form_instance})


class UserProfileView(UpdateView):

    model=UserProfile

    form_class=UserProfileFrom

    template_name="store/profile_edit.html"

    success_url=reverse_lazy("index")  #this used as as redirect
    
# @method_decorator(signin_requierd,name="dispatch")
class ProductListView(View):

    def get(self,request,*args,**kwargs):

        qs=ProductVarient.objects.all()

        return render(request,"store/productlist.html",{"products":qs})

  
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
    def get(self, request, *args, **kwargs):
        form_instance = DeliveryAdderssForm()

        return render(request, "store/deliveryaddress.html", {"form": form_instance})

    def post(self, request, *args, **kwargs):
        form_instance = DeliveryAdderssForm(request.POST)

        if form_instance.is_valid():
            
            order_summary = form_instance.save(commit=False)
            
            if request.user.is_authenticated:

                order_summary.user_object = request.user  

                order_summary.save()

                payment_method = form_instance.cleaned_data.get('payment_methode')

            if payment_method == 'cash_on_delivery':

                cart_items=request.user.cart.cart_items.filter(is_order_placed=False) #here add products to cart_items 

                order_summary_obj=OrderSummary.objects.create(                    #here create order to order summary

                user_object=request.user,

                total=request.user.cart.cart_total

        )

                for ci in cart_items:
            
                     order_summary_obj.productvarient_object.add(ci.productvarient_object)#here we can get the id of productvarient_obj that added to order summary_object--->productvarient_object

                     ci.is_order_placed=True
            
                     ci.save()
            
                     order_summary_obj.save()

                return render(request,"store/cod_delivery.html")
                
            return redirect('checkout') 
          
        
        return render(request, "store/deliveryaddress.html",{"form":form_instance})

@method_decorator(signin_requierd,name="dispatch")
class CheckOutView(View):

    def get(self,request,*args,**kwargs):

        client=razorpay.Client(auth=(KEY_ID,KEY_SECRET))

        amount=request.user.cart.cart_total*100

        data = { "amount": amount, "currency": "INR", "receipt": "order_rcptid_11" }

        payment=client.order.create(data=data)

        cart_items=request.user.cart.cart_items.filter(is_order_placed=False) #here add products to cart_items 

        order_summary_obj=OrderSummary.objects.create(                    #here create order to order summary

            user_object=request.user,

            order_id=payment.get("id"),

            total=request.user.cart.cart_total

        )

        for ci in cart_items:

            order_summary_obj.productvarient_object.add(ci.productvarient_object)#here we can get the id of productvarient_obj that added to order summary_object--->productvarient_object

            order_summary_obj.save()

        # for ci in cart_items:

        #     ci.is_order_placed=True

        #     ci.save()

        order_summary_obj.save()



        context={

            "key":KEY_ID,
            "amount":data.get("amount"),
            "currency":data.get("currency"),
            "order_id":payment.get("id")
        }

        

        return render(request,"store/payment.html",context)
    


@method_decorator(csrf_exempt,name="dispatch")    
class PaymentVerificationView(View):

    def post(self,request,*args,**kwargs):   #this post comes from razerpay


        client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))  #here razorpay Authentication

        order_summary_object=OrderSummary.objects.get(order_id=request.POST.get("razorpay_order_id"))   #here we get the id this id through we can login he user here

        login(request,order_summary_object.user_object) #

        try:

            client.utility.verify_payment_signature(request.POST)

            print("payment success")

            order_id=request.POST.get("razorpay_order_id")

            OrderSummary.objects.filter(order_id=order_id).update(is_paid=True)

            cart_items=request.user.cart.cart_items.filter(is_order_placed=False)

            for ci in cart_items:

                ci.is_order_placed=True
    
                ci.save()
        except:

                print("payment failed")
                
        return render(request,'store/success.html')

        
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

           id=kwargs.get("pk")

           product_obj=get_object_or_404(Product,id=id)

           qs=ProductVarient.objects.filter(product_object=product_obj)

           return render(request,"store/product_drop_down.html",{"products":qs})



           




    

    





    
    


    


    


    












   
    
   




        



        
    



             


                 



