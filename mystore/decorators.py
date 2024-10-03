from django.contrib import messages

from django.shortcuts import redirect



def signin_requierd(fn):

    def wrapper(request,*args,**kwargs):

        if not request.user.is_authenticated:

            messages.error(request,"invalid session please login")

            return redirect("signin")
        else:

            return fn(request,*args,**kwargs)
        
    return wrapper