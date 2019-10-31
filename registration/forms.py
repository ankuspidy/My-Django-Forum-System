from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile



class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True,)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = self.cleaned_data
        email = cleaned_data.get('email')

        try:
            user_from_db = User.objects.get(email=email)
            if user_from_db.email == email:
                raise forms.ValidationError("Email Duplitcate")
        except User.DoesNotExist:
            user_from_db = None
           # add message.error.... 
        else:
            return cleaned_data


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True,)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

        #maybe need to validate mail here also...


class ProfileUpdateForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    phone_number = forms.CharField(required=False)
    birth_day = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}) )
    summary = forms.CharField(required=False)
    posts_counter = forms.IntegerField(required=False)
    
    def __init__(self, *args, **kwargs):
       super(ProfileUpdateForm, self).__init__(*args, **kwargs)
       self.fields['posts_counter'].widget.attrs['readonly'] = True

    class Meta:
        model = Profile
        fields = ['posts_counter', 'phone_number', 'birth_day', 'social_media', 'summary']

        labels = {
              "posts_counter": "Number of Posts",
          }

    # def clean(self):
    #     cleaned_data = self.cleaned_data


    #     try:
    #         profile_from_db = Profile.objects.get(nickname=nickname)
    #         print("nickfromdb: ", profile_from_db.nickname)
    #         if profile_from_db.nickname == nickname:
    #             raise forms.ValidationError("Nickname Duplitcate")
    #     except Profile.DoesNotExist:
    #         profile_from_db = None
    #        # add message.error.... 
    #     else:
    #         return cleaned_data

