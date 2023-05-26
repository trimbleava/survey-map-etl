from django import forms

# app modules
from tenants.models import UploadFile


class UploadFileModelForm(forms.ModelForm):
    class Meta:
        model = UploadFile
        fields = ('title', 'filename')


class UploadFileForm(forms.Form):
    title = forms.CharField(label="Unique Title", help_text="Enter a unique title")
    # filename = forms.FileField(label="File Name", help_text="Select a file to upload")  # single file
    filename = forms.FileField(label="File Name", help_text="Select a file to upload",
        widget=forms.ClearableFileInput(attrs={"multiple": True, "type": "file"})
    )
    
# For single file
# fname =  request.FILES['file_field'].name
# folder = self.request.tenant.slug
# full_filename = os.path.join(settings.MEDIA_ROOT, folder, fname)
# fout = open(full_filename, 'wb+')
# fout.write(request.FILES['file_field'].read())
# fout.close()