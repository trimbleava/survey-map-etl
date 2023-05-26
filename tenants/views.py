# standard libs
import os, sys
import inspect
import types
import importlib
import json

# third party libs
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.views.generic import FormView, TemplateView, CreateView
from django.core.serializers import serialize
from django.core.management import call_command
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from django.db.utils import DatabaseError
# from django.core.cache import cache
#
from django_tenants.urlresolvers import reverse_lazy
#
import pandas as pd  

# app modules
from customers.forms import GenerateUsersForm
from customers.models import Client
from customers.models import USAStates
#
from tenants.models import UploadFile
from tenants.forms import UploadFileForm, UploadFileModelForm
from heath_lsa import django_utils as djutil 
#
from system_modules import sys_utils

import logging
logger = logging.getLogger('lsajang')  # see settings

#
# Pre condition:
# Check for the value of the submit button in any self.request.POST, 
# and return the appropriate url.
# reverse(viewname, urlconf=None, args=None, kwargs=None, current_app=None)
# path('archive/', views.archive, name='news-archive')
# using the named URL - reverse('news-archive')
# passing a callable object: reverse(views.archive) - Not recommended
#  TODO
# <form action="" method="post">
#    {% csrf_token %}
#    {{ form.as_p }}
#    <input type="submit" value="Speichern" name="save"/>
#    <input type="submit" value="Speichern & weiter" 
#        name="save_and_continue"/>
#</form>
#
def get_success_url(request, pk):
    if request.POST.get('save'):
        return reverse('success_url_for_save')
    elif request.POST.get('save_and_continue'):
        return reverse('success_url_for_save_and_continue', kwargs={'pk': pk})
    else:
        return reverse('fallback_success_url')


#
# Class attributes are evaluated on import, So, If we are using
# 'success_url=xxx' in a class we have to use reverse_lazy() and if
# we are reversing inside a function we can use reverse()  TODO
#
# class NewJobCBV(LoginRequiredMixin, CreateView):
#     template_name = 'company/job.html'
#     form_class = newJobForm
#     # success_url = reverse_lazy('newJob')

#     def get_success_url(self, **kwargs):
#         return reverse("newJob")


def region_view(request):
    msg = f"Entered {__name__}\n"
    logger.info(msg)

    # this only should set using session because it only goes
    # to environ when slugobj is activate. In TenantHomeView
    # we only read config but not set the environ!! So, adjust
    # accordingely, if needed geion to be in environ.
    region = request.session.get('region')
    data=serialize('geojson', USAStates.objects.filter(name=region).all(), geometry_field='geom')

    return HttpResponse(data, content_type='json')
    
#
# If you want to run some code on every tenant you can do the following
#
# from django_tenants.utils import tenant_context, get_tenant_model
#
#for tenant in get_tenant_model().objects.all():
#    with tenant_context(tenant):
#        pass
#        # do whatever you want in that tenant


# def generate_model(shpfile, path_to_models, modelname, geom, srid):
#     call_command(ogrinspect, shpfile, modelname, geom_name=geom, mapping=False, 
#                                            srid=srid, stdout=f, verbosity=False, multi_geom=True )
#     python manage.py makemigrations southwestgaslv
#     python manage.py migrate_schemas --schema=southwestgaslv_1680701229


#
# TemplateView should be used when you want to present 
# some information in a html page. TemplateView shouldn't 
# be used when your page has forms and does creation or 
# update of objects. In such cases FormView, CreateView 
# or UpdateView is a better option
#
class TenantHomeView(TemplateView):
    """
        This is the case where the latest created map is displayed on the home page
        by reading the data from the cache as defined in the survey_name variable. 
        if cache exists and the survey_name does not exists, displays an error msg
        to the user. Note: this case should not happen but for system error!
        If cache is cleared, even the region should not exist and display should be
        only the county map.

    Args:
        TemplateView (_type_): _description_

    Returns:
        _type_: _description_
    """
    template_name = 'index_tenant.html'

    msg = "Entered TenantHomeView\n"
    logger.info(msg)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
    
        # always available in the request object
        context["slug"] = self.request.tenant.slug             # southwestgaslv
        context["schema"] = self.request.tenant.schema_name    # southwestgaslv_1676228649
        context["tenant"] = self.request.tenant.name           # South West Gas - LA"
        context["geoe_url"] = os.getenv("GEOSERVER_URL")       # required by js for legends
       
       
        if djutil.session_is_expired(self.request):
            print("Session is expired -- TODO")
        else:
            print("Session is not expired -- TODO")
        
        #
        # for checking cache vs session
        #
        djutil.print_sessions(self.request)
        #
        # Note: when cache is empty and this method is we get this error! 
        # "The request's session was deleted before the request completed"
        # which I do not know why??
        #
        # djutil.print_sessioncache(self.request)

        active_cfg = self.request.session.get("survey_name", None)
        if active_cfg is None:
            msg = "An active survey map config file was not found, please run a survey map\n"
            messages.add_message(self.request, messages.WARNING, msg)
        
        #
        # The config info (variables) are saved in the session or cache. 
        # The data itself is saved in geoserver datastores to grab and display.
        #
        cached_dict = djutil.get_backend_cache(self.request)

        if len(cached_dict) == 0 :
            djutil.set_session(self.request, context, overwrite=False)
            return djutil.display_helper(self.request, context)

        context["region"] = cached_dict.get("region", None)
        context["survey_copyright"] = cached_dict.get("survey_copyright", None)
        #  
        # use the cached data to rebuild the context approriate for html/js
        # in order to display the latest available survey map, if any
        #
        if cached_dict.get("ovlayers_status") == 1:

            # check the store in geoserver to see if the layers exist TODO
            # if exist, format the context for display 
            context["ovlayers_bbox"] = cached_dict.get("ovlayers_bbox")
            context["ov_style"] = cached_dict.get("ov_style")
            context["ovlayers_status"] = cached_dict.get("ovlayers_status")
        else:
            msg = "No Overlay map is detected, please run a Overlay map\n"
            messages.add_message(self.request, messages.WARNING, msg)

        if cached_dict.get("oplayers_status") == 1: 

            # check the store in geoserver to see if the layers exist TODO
            # attribute = geoe.get_feature_attribute(feature_type_name, workspace, op_store_name)
            # print(attribute)
            #
            # if exist, format the context for display    
            context["oplayers_bbox"] = cached_dict.get("oplayers_bbox")
            context["op_style"] = cached_dict.get("op_style")
            context["oplayers_status"] = cached_dict.get("oplayers_status")
        else:
            msg = "No Survey map is detected, please run a Survey map\n"
            messages.add_message(self.request, messages.WARNING, msg)    
        #
        # test
        # Use JSON dump so that it will be a data that can be loaded in javascript
        # context = {
        #     'dict_1': json.dumps({
        #         'key_1': ['val_11', 'val_12'], 'key_2': ['val_21', 'val_22']
        #     })
        # }
        # # template
        # {{dict_1 | json_script:"dict_id"}}
        # # js
        # var js_dict = JSON.parse(document.getElementById('dict_id').textContent);
        # console.log(js_dict);
            
        djutil.set_session(self.request, context, overwrite=True)
        return djutil.display_helper(self.request, context)
            
            
class DisplaySurveyMapView(TemplateView): 
    template_name = 'create_overlay.html'

    msg = "Entered DisplaySurveyMapView\n"
    logger.info(msg)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info(self.request.session)
        
        return djutil.display_helper(self.request, context)


class CreateSurveyMapView(TemplateView):
    msg = "Entered CreateSurveyMapView\n"
    logger.info(msg)

    template_name = 'create_surveymap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
       
        path = self.request.path.split("/")    # TODO: find how to get the asgi shakhand connection and use directly in js
        iden = path[-2:-1][0]
        if iden == "createsurveymap":
            context['url_ws_identifier'] = "/ws/survey-map/" 
            context["surveymap_title"] = "Creating Survey Map For "
        elif iden == "createoverlay":
            context['url_ws_identifier'] = "/ws/overlay-map/"
            context["surveymap_title"] = "Creating Overlay Map For "

        # always available in the request object
        slug = self.request.tenant.slug             # southwestgaslv
        schema = self.request.tenant.schema_name    # southwestgaslv_1676228649
        tenant = self.request.tenant.name           # South West Gas - LA"
        tenant_dir = os.getenv("TENANT_DIR")

        # this function is duplicated due to not being able to pass the slugobj to session
        cfg = sys_utils.get_customer_config(slug, tenant_dir)  
        if cfg.startswith("Error"):
            msg = "Please provide a valid configuration file and re-run your maps.\n"
            msg += cfg
            messages.add_message(self.request, messages.ERROE, msg) 

        #
        # saving variables into context for passing to js/html usage
        #
        context["slug"] = slug 
        context["schema"] = schema
        context["tenant"] = tenant
        context["tenant_dir"] = os.getenv("TENANT_DIR")

        #
        # setting session items for passing into channel consumer
        #
        djutil.set_session(self.request, context, overwrite=True)

        # djutil.print_sessions(self.request)
        djutil.print_sessioncache(self.request)

        return djutil.display_helper(self.request, context)
      

class CreateOverlayView(TemplateView): 
    template_name = 'create_overlay.html'

    msg = "Entered CreateOverlayView\n"
    logger.info(msg)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info(self.request.session)

        # always available in the request object
        slug = self.request.tenant.slug             # southwestgaslv
        schema = self.request.tenant.schema_name    # southwestgaslv_1676228649
        tenant = self.request.tenant.name           # South West Gas - LA"

        cfg = sys_utils.get_customer_config(slug, os.getenv("TENANT_DIR"))
        if cfg.startswith("Error"):
            msg = "Please provide a valid configuration file and re-run your maps.\n"
            msg += "The displayed layers, if any, many not be in compliance with expected goal.\n"
            msg += cfg
            messages.add_message(self.request, messages.ERROE, msg) 
            context["active_cfg"] = None

        else:       
            logger.info(f"Reading active config file {cfg}")

            data_dict = sys_utils.read_customer_config(cfg)
            context["active_cfg"] = cfg

            region           = data_dict["CUSTOMER_REGION"]
            survey_copyright = data_dict["SURVEY_COPYRIGHT"]
            survey_name      = data_dict["SURVEY_NAME"]

            #
            # saving variables into context for passing to js/html usage
            #
            context["region"] = region
            context["slug"] = slug  
            context["survey_copyright"] = survey_copyright
            context["survey_name"] = survey_name
            context["schema"] = schema
            context["tenant"] = tenant
            context["tenant_dir"] = os.getenv("TENANT_DIR")

            #
            # extract the overlay layers into context, also need bounding box
            #
            context["overlay_dict"] = {}  
            overlay_fcs = data_dict["Overlay"]
            for fc, geom,include,filter,legend in overlay_fcs:
                # this is by design for passing to map
                context["overlay_dict"][fc] = "overlay_dict" 
    
            #
            # get the operational layers into context
            #
            context["operational_dict"] = {}
            operational_fcs = data_dict["Operational"]
            for fc, geom,include,filter,legend in operational_fcs:
                # this is by design for passing to map
                context["operational_dict"][fc] = "operational_dict" 
        
            #
            # get the survey types into context - TODO
            #
            context["surveytype_dict"] = {}
    
            #
            # the bbox for the overlay layers are processed in the survey map consumer
            #
            try:
                ovbbox = self.request.session["ovlayers_bbox"] 
                if ovbbox:
                    context["ovlayers_bbox"] = ovbbox
                ovstatus = self.request.session["ovlayers_status"]  # coming from consumer
            except Exception as e:
                logger.warning(f"OVBox not in session: {str(e)}")

        #
        # setting session items for passing into channel consumer
        #
        djutil.set_session(self.request, context, overwrite=True)

        djutil.print_sessions(self.request)
        djutil.print_sessioncache(self.request)

        return djutil.display_helper(self.request, context)


class DeleteOverlayView(TemplateView): 
    """Deletes overlay layers from the Overlay datastore
       reading from the configuration file. 
       Updates the view with remaining, if any, layers,
       including the legends.
    Args:
        TemplateView (_type_): _description_

    Returns:
        _type_: _description_
    """
    template_name = 'delete_overlay.html'

    msg = "Entered DeleteOverlayView\n"
    logger.info(msg)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info(self.request.session)

        # regardless of session information, must read config and 
        # ask for deletion and delete and do not change the current
        # session
        slug = self.request.tenant.slug
        cfg = sys_utils.get_customer_config(slug)
        data_dict = sys_utils.read_customer_config(cfg)
        region = data_dict["CUSTOMER_REGION"]
        survey_copyright = data_dict["SURVEY_COPYRIGHT"]
        geoe_url = os.getenv("GEOSERVER_URL")
        
        #
        # saving variables into context for passing to js/html usage
        #
        context["region"] = region
        context["geoe_url"] = geoe_url
        context["slug"] = slug  
        context["survey_copyright"] = survey_copyright
    
        #
        # get the overlay layers into context, also need bounding box
        # but they are not ready until after invoking overlay view.
        # we also need the categorized version in context for map
        #
        context["overlay_dict"] = {}  
        overlay_fcs = data_dict["Overlay"]
        for fc, geom,include,filter,legend in overlay_fcs:
            # this is by design for passing to map
            context["overlay_dict"][fc] = "overlay_dict" 
        # 
        # remove the control from the map - TO DO
        #

        return djutil.display_helper(self.request, context)



class CreateOverlayLegendView(TemplateView):
    msg = "Entered CreateOverlayLegendView\n"
    logger.info(msg)

    template_name = 'under_construction.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        djutil.set_session(self.request)
        return djutil.display_helper(self.request, context)


class CreateSurveyMapView2(TemplateView):
    msg = "Entered CreateSurveyMapView\n"
    logger.info(msg)
    # template_name = 'under_construction.html'
    template_name = 'create_surveymap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_ws_identifier'] = "/ws/op/"

        # keep this for future
        # path = self.request.path.split("/")    # TODO: find how to get the asgi shakhand connection and use directly in js
        # iden = path[-2:-1][0]
        # if iden == "models":
        #     context['url_ws_identifier'] = "/ws/op/models" 
        # elif iden == "migrations":
        #     context['url_ws_identifier'] = "/ws/op/migrations"
        # elif iden == 'loaddata':
        #     context['url_ws_identifier'] = "/ws/op/loaddata"

        djutil.set_session(self.request, context)
        return djutil.display_helper(self.request, context)

#
# TemplateView should be used when you want to present 
# some information in a html page. TemplateView shouldn't 
# be used when your page has forms and does creation or 
# update of objects. In such cases FormView, CreateView 
# or UpdateView is a better option TODO: template multi files
#
class FileUploadFormView(FormView):
    msg = "Entered FileUploadFormView\n"
    logger.info(msg)

    form_class = UploadFileForm
    template_name = "upload_file.html"  
    success_url = reverse_lazy('save-survey-config')  # back to same page

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist("filename") 
        if form.is_valid():
            folder = self.request.tenant.slug
            # construct the output location of the file
            try:
                out_dir = os.path.join(settings.MEDIA_ROOT, folder)
            except:
                pass
            for f in files:
                msg = djutil.handle_uploaded_file(f, out_dir)
                messages.add_message(request, messages.SUCCESS, msg)

            return self.form_valid(form)
            
        else:
            msg = "Form did not pass validation!"
            messages.add_message(request, messages.ERROR, msg)
            return self.form_invalid(form)


class FileUploadView(CreateView):
    msg = "Entered FileUploadView\n"
    logger.info(msg)

    template_name = "upload_file.html"
    form_class = UploadFileModelForm
    success_url = reverse_lazy('save-survey-config')

    def post(self, request, *args, **kwargs): 
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "File uploaded")
            return self.form_valid(form)

        else:
            msg = "Form did not pass validation!"
            messages.add_message(request, messages.ERROR, msg)
            return self.form_invalid(form)    


def generate_model_view(request): 
    msg = "Entered generate_model_view\n"
    logger.info(msg)

    try:
        # running management command load_usa_bounds
        # python manage.py tenant_command load_usa_bounds --schema=public or tenant
        # tenant_command is not callable, just frim command line!!
        call_command('generate_model')
        msg = f"Generated model {model}" 
        messages.add_message(request, messages.SUCCESS, msg)
    except Exception as e:
        msg = str(e)
        print(msg)
        messages.add_message(request, messages.ERROR, msg)
    return redirect('home-public')  


class TenantViewRandomForm(FormView):
    msg = "Entered TenantViewRandomForm\n"
    logger.info(msg)

    form_class = GenerateUsersForm
    template_name = "random_form.html"
    success_url = reverse_lazy('random_form')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tenants_list'] = Client.objects.all()
        context['users'] = User.objects.all()
        return context

    def form_valid(self, form):
        User.objects.all().delete()  # clean current users

        # generate five random users
        users_to_generate = 5
        first_names = ["Aiden", "Jackson", "Ethan", "Liam", "Mason", "Noah",
                       "Lucas", "Jacob", "Jayden", "Jack", "Sophia", "Emma",
                       "Olivia", "Isabella", "Ava", "Lily", "Zoe", "Chloe",
                       "Mia", "Madison"]
        last_names = ["Smith", "Brown", "Lee", "Wilson", "Martin", "Patel",
                      "Taylor", "Wong", "Campbell", "Williams"]

        while User.objects.count() != users_to_generate:
            first_name = choice(first_names)
            last_name = choice(last_names)
            try:
                user = User(username=(first_name+last_name).lower(),
                            email="%s@%s.com" % (first_name, last_name),
                            first_name=first_name,
                            last_name=last_name)
                user.save()
            except DatabaseError:
                pass

        return super().form_valid(form)




