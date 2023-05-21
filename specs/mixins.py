from django.http.response import HttpResponseRedirect
from django.views.generic import View



class SecurityMixin(View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # This will redirect to the login view
            return HttpResponseRedirect('/login/')
        if not self.request.user.is_staff:
            # Redirect the user to somewhere else - add your URL here
            return HttpResponseRedirect('/')
        return super().dispatch(request, *args, **kwargs)