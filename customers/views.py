
# standard libraries
import os

# third part libraries
from django.contrib import messages
from django.core.management import call_command
from django.conf import settings
from django.db import utils
from django.views.generic import FormView, TemplateView, CreateView
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
#
from tenant_users.tenants.utils import create_public_tenant, get_current_tenant
from tenant_users.tenants.tasks import provision_tenant
#
from django_tenants.utils import remove_www
from django_tenants.urlresolvers import reverse_lazy
from django_tenants.management.commands import tenant_command

# app modules
from customers.forms import AddPublicTenantForm, AddTenantForm
from customers.models import Client
from customers.models import USAStates
from accounts.models import TenantUser

import logging
djlogger = logging.getLogger('lsajang')  # see settings

#
# Leave this alone! not tested if can be exchanged with
# generic display_helper in utils due to no customer case!
#
def display_helper(request, context=None):
    if not context:
        context = {}
   
    hostname_without_port = remove_www(request.get_host().split(':')[0])
  
    try:
        Client.objects.get(schema_name='public')
    except utils.DatabaseError:
        context['need_sync'] = True
        context['shared_apps'] = settings.SHARED_APPS
        context['tenants_list'] = []
        return context
    except Client.DoesNotExist:
        context['no_public_tenant'] = True
        context['hostname'] = hostname_without_port

    if Client.objects.count() == 1:
        context['only_public_tenant'] = True

    context['tenants_list'] = Client.objects.all()
    return context


# redirect success url or any message page
class MessagPageView(TemplateView):
    template_name = "lsa_messages_page.html"
    # messages are usually send before this gets here
    # if need more control add the context or get methods
   

class LoadNationalBoundsDataView(TemplateView):
    # EXAMPLE of passing messages into the generic lsa_messages
    def get(self, request, *args, **kwargs):
        # could not figur it out how to pass the title in redirect/reverse!!
        request.session['title'] = "Load National Boundaries Data"
        try:
            # running management command load_usa_bounds
            # python manage.py tenant_command load_usa_bounds --schema=public or tenant
            # call_command('load_usa_bounds')
            msg = f"Populated national boundaries dataset"
            messages.add_message(request, messages.SUCCESS, msg)        
        except Exception as e:
            msg = str(e)
            messages.add_message(request, messages.ERROR, msg)
        return redirect('lsa-messages')


def load_national_bounds_data(request):
    try:
        #
        # pre conditions: makemigrate, migrate_schemas
        # running management command load_usa_bounds
        # python manage.py tenant_command load_usa_bounds --schema=public or tenant
        # tenant_command is not callable, just frim command line!!
        call_command('load_usa_bounds')
        msg = f"Populated national boundaries dataset" 
        messages.add_message(request, messages.SUCCESS, msg)
    except Exception as e:
        msg = str(e)
        print(msg)
        messages.add_message(request, messages.ERROR, msg)
    return redirect('home-public')  
    
      
class HomeView(TemplateView):
    template_name = "index_public.html"
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return display_helper(self.request, context)


class AddPublicTenantView(TemplateView):
    template_name = "addtenant_public.html"

    def get_context_data(self, **kwargs):
        context = super(AddPublicTenantView, self).get_context_data(**kwargs)
        form = AddPublicTenantForm(self.request.POST or None)
        context["form"] = form
        return context


    def post(self, request, *args, **kwargs):
        context = self.get_context_data()   
        form = context["form"]
        if form.is_valid():
            # post the form and get the populated form data back
            domain_url = form.cleaned_data['domain_url']
            owner_email = form.cleaned_data['owner_email']

            # execute the method
            msg = ""
            try:
                # example: from tenant_users.tenants.utils import create_public_tenant
                # create_public_tenant(domain_url="my.evilcorp.domain", owner_email="admin@evilcorp.com")
                #
                create_public_tenant(domain_url=domain_url, owner_email=owner_email)
                # TODO - update request???
                msg = f"Added public Tenant."   
            except Exception as e:
                msg = str(e)
                print(msg)
                messages.add_message(request, messages.ERROR, msg)
                return HttpResponseRedirect(request.path_info)
            messages.add_message(request, messages.SUCCESS, msg)
            return HttpResponseRedirect(request.path_info)             
        else:
            messages.add_message(request, messages.ERROR, f'{form.errors}')
            return HttpResponseRedirect(request.path_info)
            

class AddTenantView(TemplateView):
    template_name = "addtenant.html"

    def get_context_data(self, **kwargs):
        context = super(AddTenantView, self).get_context_data(**kwargs)
        form = AddTenantForm(self.request.POST or None)
        context["form"] = form
        return display_helper(self.request, context)
        

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()   
        form = context["form"]

        if form.is_valid():
            tenant_name = form.cleaned_data['tenant_name']
            tenant_slug = form.cleaned_data['tenant_slug']
            user_email = form.cleaned_data['user_email']
            user_password = form.cleaned_data['user_password']
            # user_is_active = form.cleaned_data['user_is_active']
            msg = ""
            try:
                user = TenantUser.objects.create_user(email=user_email, password=user_password, is_active=True)
                tenant = provision_tenant(tenant_name=tenant_name, tenant_slug=tenant_slug, user_email=user_email)
                msg = f"Added {tenant_name} Tenant." 
                messages.add_message(request, messages.SUCCESS, msg)
                return HttpResponseRedirect(request.path_info)  

            except Exception as e:
                msg = "Something went wrong!"
                messages.add_message(request, messages.SUCCESS, msg)
                return HttpResponseRedirect(request.path_info)   
        else:
            # send error message to user
            # messages.error(request, f'{form.errors}')
            messages.add_message(request, messages.ERROR, f'{form.errors}')
            return HttpResponseRedirect(request.path_info)


