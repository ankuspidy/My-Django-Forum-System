from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth.views import FormView, PasswordResetView
from django.contrib.auth.models import User


from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .forms import UserRegistrationForm, ProfileUpdateForm
from my_django_forum.settings import DEFAULT_FROM_EMAIL


def home(request):
    context = {}
    html = '<h1>Hello World</h1>'
    return HttpResponse(html)

class RegisterFormView(FormView):
    template_name = 'registration/register.html'

    def get(self, request, *args, **kwargs):
        user_form = UserRegistrationForm()
        profile_form = ProfileUpdateForm()

        return render(request, 'registration/register.html', {'user_form': user_form, 'profile_form':profile_form})
    
    def post(self, request, *args, **kwargs):

        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileUpdateForm(request.POST)#, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            
            profile_form.instance = user_form.instance.profile
            profile_form.instance.phone_number = profile_form.cleaned_data.get('phone_number')
            profile_form.instance.nickname = profile_form.cleaned_data.get('nickname')

            profile_form.save()
            #messages.success(request, 'הפרופיל נוצר! ניתן כעת להתחבר לאתר.')
            return redirect('home')

        else:
            print("error: ", user_form.errors)
            user_form = UserRegistrationForm(request.POST)
            profile_form = ProfileUpdateForm(request.POST)

            return render(request, 'registration/register.html', {'user_form': user_form, 'profile_form':profile_form})

class UserPasswordResetView(PasswordResetView):
    template_name = "registration/password_reset.html"

    def post(self, request, *args, **kwargs):
        subject_template_name = 'registration/password_reset_subject.txt'
        email_template_name = 'registration/password_reset_email.html'

        requested_user = User.objects.get(email=request.POST['email'])

        context = {
            'request': request,
            'protocol': request.scheme,
            'user': requested_user,
            'domain': request.META['HTTP_HOST'],
            'uid': urlsafe_base64_encode(force_bytes(requested_user.pk)),
            'token': default_token_generator.make_token(requested_user)
        }

        html_loader = get_template(email_template_name)
        html_content = html_loader.render(context)
        subject = render_to_string(subject_template_name)
        subject = ''.join(subject.splitlines())
        message = EmailMultiAlternatives(subject, '', DEFAULT_FROM_EMAIL, [requested_user.email])
        message.attach_alternative(html_content, "text/html")
        message.send()

        return redirect('password_reset_done')     



