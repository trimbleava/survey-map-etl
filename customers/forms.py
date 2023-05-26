from django import forms
from django.forms import ModelForm, Form
from tenant_users.tenants.utils import create_public_tenant
from tenant_users.tenants.tasks import provision_tenant

# app modules


# Workflow:
# calls:
# ==> UserModel = get_user_model()
# ==> TenantModel = get_tenant_model()
# ==> public_schema_name = get_public_schema_name()
# Create public tenant user. This user doesn't go through object manager
# create_user function because public tenant does not exist yet
# ==> profile=UserModel(email=owner_email,is_active,**owner_extra, unusable_password).save
# Create public tenant
# ==> public_tenant=TenantModel(schema_name,name='Public Tenant', owner=profile)
# Add one or more domains for the tenant
# ==> get_tenant_domain_model(domain=domain_url,tenant=public_tenant,is_primary=True)
# Add system user to public tenant (no permissions):
# ==> public_tenant.add_user(profile,is_superuser=False, is_staff=False) <== tenant_users.tenants.models <== TenantBase(TenantMixin)
# ==> UserTenantPermissions() tenant permission
# ==> Link user to tenant
class AddPublicTenantForm(Form):
    # field_name = models.Field(option = value)
    # field_name = models.Field(widget=forms.Textarea, label='Your name', initial='Your name', 
    #                            help_text='100 characters max.', auto_id=False, max_length=100,
    #                            error_messages={'required': 'Please enter your name'},
    #                            required=True)
    #
    # local dev tenants	
	# 127.0.0.1	lsa.etl.heathus.domain        	# public
	# 127.0.0.1	swg.lsa.etl.heathus.com		    # tenant
	# TENANT_USERS_DOMAIN = "lsa.etl.heathus.com"
    # add lsa.etl.heathus.com to host in setting
    # domain_url="my.evilcorp.domain", owner_email="admin@evilcorp.com"
    #
    
    # initial="public.lsa.etl.heathus.com",
    domain_url=forms.CharField( help_text="Preset domain for tenant users (i.e. public.lsa.etl.heathus.com)",
                                label="Domain URL")   
    # initial="admin@lsa.etl.heathus.com"
    owner_email=forms.CharField( help_text="Email belong to owner of public tenant (i.e. admin@lsa.etl.heathus.com)",
                                 label="Owner Email")


class AddTenantForm(Form):
    tenant_name=forms.CharField(help_text="Heath customer's name (i.e. South West Gas)",
                                label="Tenant Name")       
    tenant_slug=forms.CharField(help_text="Tenant URL name, only ascii characters", label="Slug")
    #                            widget=forms.HiddenInput())
    user_email=forms.CharField(help_text="Preset email belong to this tenant (i.e. admin@swglv.com)",
                               label="Tenant User Email")
    user_password=forms.CharField(label='Password', widget=forms.PasswordInput(), required=True)
    # user_is_active=forms.BooleanField(help_text="Tenant user account status. Default: active",
    #                                 label="Is Active")


class GenerateUsersForm(Form):
    pass