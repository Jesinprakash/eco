from django import forms

from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm

from mystore.models import UserProfile,OrderSummary,Reviews


class RegistrationForm(UserCreationForm):

    password1=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control mb-3"}))

    password2=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control mb-3"}))


    class Meta:

        model=User

        fields=["username","email","password1","password2"]

        widgets={

            "username":forms.TextInput(attrs={"class":"form-control mb-3"}),

            "email":forms.EmailInput(attrs={"class":"form-control mb-3"}),

        }

class LoginForm(forms.Form):

    username=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control mb-2"}))

    password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control mb-2"}))

class UserProfileFrom(forms.ModelForm):

    class Meta:

        model=UserProfile

        fields=["bio","pro_pic"]

        widgets={
            'bio':forms.TextInput(attrs={'class':'w-full border my-5 p-2'}),
            'profile_picture':forms.FileInput(attrs={'class':'w-full border my-5 p-2'})
        }


class DeliveryAdderssForm(forms.ModelForm):

    class Meta:

        model=OrderSummary

        fields=["name","phone","email","pin","delivery_address","payment_methode"]

        widgets={

            "name":forms.TextInput(attrs={'class':'form-control border mb-2 '}),

            "phone":forms.TextInput(attrs={'class':'form-control border mb-2'}),

            "email":forms.EmailInput(attrs={'class':'form-control border mb-2'}),

            "pin":forms.NumberInput(attrs={'class':'form-control border mb-2'}),
            
            "delivery_address":forms.Textarea(attrs={'class':'form-control border mb-2','rows':3}),
            
            "payment_methode":forms.Select(attrs={'class':'form-control border mb-2'})
        }


class ReviewForm(forms.ModelForm):

        class Meta:

            model=Reviews

            fields=["comment","rating"]

            widgets={

                "comment":forms.Textarea(attrs={'class':'form-control border  mb-2','rows':3}),

                "rating":forms.TextInput(attrs={'class':'border dark'})
            }




