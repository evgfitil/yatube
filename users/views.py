from django.views.generic import CreateView
from .forms import CreationForm
# Create your views here.


class SignUp(CreateView):
    form_class = CreationForm
    success_url = "/auth/login"
    template_name = "signup.html"
