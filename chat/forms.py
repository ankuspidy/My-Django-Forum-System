from .models import Message
from django.forms import ModelForm, HiddenInput, TextInput

class NewMessageForm(ModelForm):
  
    class Meta:
        model = Message
        fields = ['message_body']
        widgets = {
          'message_body': TextInput(),
          'author': HiddenInput(),
          'recipient': HiddenInput(),
          'date_time': HiddenInput(),
          'read_status': HiddenInput(),
        }

        labels = {
            "message_body": "",
        }