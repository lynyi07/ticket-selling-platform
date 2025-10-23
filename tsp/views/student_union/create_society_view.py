from django.shortcuts import render, redirect
from django.views import View  
from tsp.views.helpers import StudentUnionAccessMixin 
from tsp.forms.student_union.create_society_form import CreateSocietyForm
import re
from tsp.models import Domain
from django.contrib import messages

class CreateSocietyView(StudentUnionAccessMixin, View):
    """View that allows a student union to create a society."""
    
    template_name = 'student_union/create_society.html'
    http_method_names = ['get', 'post']

    def get(self, request):
        """
        Handle the GET request to the create society view.

        Parameters
        ----------
        request : HttpRequest
            The request object for the HTTP request.

        Returns
        -------
        HttpResponse
            A response to the create society page.
        """

        form = CreateSocietyForm() 
        return self.render(form)

    def post(self, request):
        """"
        Handle and validate the POST request of create society view.
        
        Parameters
        ----------
        request : HttpRequest
            The request object for the HTTP request.

        Returns
        -------
        HttpResponse or HttpRedirect
            A redirected response to the view societies page if form is valid,
            otherwise return a redirected response to the view societies page.
        """
        
        form = CreateSocietyForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            domain_name = re.findall("@[a-zA-Z0-9.]*", email)[0][1:]
            university_domain = Domain.objects.get(name=domain_name)
            if request.user.university == university_domain.university:
                form.save()
                messages.add_message(
                    request, 
                    messages.SUCCESS, 
                    f"Society: {form.cleaned_data.get('name')} successfully created!"
                )
                return redirect("view_societies")
            else:
                form.add_error('email', 'Domain is not valid')
        # Reload the form if it is invalid
        return self.render(form) 
        
    def render(self, form): 
        """
        Render the create society template with the provided form.

        Parameters
        ----------
        form : CreateSocietyForm
            The form object to render in the template.

        Returns
        -------
        HttpResponse
            A response containing the rendered create society template.
        """
            
        return render(self.request, self.template_name, {'form':form}) 