from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib import messages

from auth_app.forms import SignUpForm


class SignUp(FormView):
    template_name = 'registration/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('auth_app:Login')

    def form_valid(self, form):
        form.save()
        return super(SignUp, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, form.errors)
        return super(SignUp, self).form_invalid(form)
