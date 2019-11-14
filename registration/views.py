from django.shortcuts import render, redirect
from django.contrib.auth.views import FormView, PasswordResetView
from django.views.generic import DetailView ,ListView
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile
from my_django_forum.settings import DEFAULT_FROM_EMAIL


class RegisterFormView(FormView):
    template_name = 'registration/register.html'

    def get(self, request, *args, **kwargs):
        user_form = UserRegistrationForm()
        profile_form = ProfileUpdateForm()
        context = dict(user_form=user_form, profile_form=profile_form)
        
        return render(request, 'registration/register.html', context)
    
    def post(self, request, *args, **kwargs):

        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileUpdateForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
               
                user_form.save()
                profile_form.instance = user_form.instance.profile
                profile_form.instance.phone_number = profile_form.cleaned_data.get('phone_number')
                profile_form.instance.birth_day = profile_form.cleaned_data.get('birth_day')
                profile_form.instance.social_media = profile_form.cleaned_data.get('social_media')
                profile_form.instance.summary = profile_form.cleaned_data.get('summary')
                profile_form.save()
                messages.success(request, 'Your profile has been created! You may login!')

                return redirect('login')

        else:
            print("error: ", user_form.errors)
            user_form = UserRegistrationForm(request.POST)
            profile_form = ProfileUpdateForm(request.POST)
            context = dict(user_form=user_form, profile_form=profile_form)
           
            return render(request, 'registration/register.html', context)

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

class ProfileFormView(FormView):
    template_name = 'registration/profile.html'

    def get(self, request, *args, **kwargs):
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        context = dict(user_form=user_form, profile_form=profile_form)

        return render(request, 'registration/profile.html', context)
    
    def post(self, request, *args, **kwargs):

        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile )

        operation_result = None
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile Has Been Updated!')
            operation_result = redirect('profile')
        else:
            print("error: ", user_form.errors)
            user_form = UserRegistrationForm(request.POST, instance=request.user)
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
            context = dict(user_form=user_form, profile_form=profile_form)

            operation_result = render(request, 'registration/profile.html', context)

        return operation_result

class UserProfileView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'registration/user_profile.html'

    def get(self, request, *args, **kwargs):
        super(UserProfileView, self).get(request, *args, **kwargs)
        context = self.get_queryset()
        operation_result = None
        
        if self.request.user.username == self.kwargs['user']:
            operation_result = redirect('profile')
        else:
            operation_result = render(request, 'registration/user_profile.html', {'user_profile' : context})

        return operation_result

    def get_queryset(self):
        queryset = User.objects.get(username=self.kwargs['user'])

        return queryset
