"""The views that takes care of authantication."""
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView

from buildservice.utils.decorators import anonymous_user_required


@method_decorator(anonymous_user_required, name='dispatch')  # pylint: disable=too-many-ancestors
class RegisterView(CreateView):
    """
    A view for registering a new user for the app.
    It'll register to the home view upon success.
    """

    def form_valid(self, form):
        """
        This method is called after the form is validated,
        meaning the user is created. Django doesn't authenticate
        him automatically, we have to do it.
        """
        response = super(RegisterView, self).form_valid(form)
        user = authenticate(
            username=self.object.username,
            password=form.cleaned_data['password1']
        )
        if user:  # means user is authenticated
            login(self.request, user)
        return response
