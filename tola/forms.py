import os

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User

from tola import DEMO_BRANCH
from workflow.models import TolaUser, TolaBookmarks, Organization


class RegistrationForm(UserChangeForm):
    """
    Form for registering a new account.
    """
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('initial')
        super(RegistrationForm, self).__init__(*args, **kwargs)
        del self.fields['password']
        self.fields['tola_user_uuid'].widget = forms.HiddenInput()
        # if they aren't a super user or User Admin don't let them change countries form field
        if 'User Admin' not in user['username'].groups.values_list('name', flat=True) and not user['username'].is_superuser:
            self.fields['countries'].widget.attrs['disabled'] = "disabled"
            self.fields['country'].widget.attrs['disabled'] = "disabled"

    class Meta:
        model = TolaUser
        fields = '__all__'

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-6'
    helper.form_error_title = 'Form Errors'
    helper.error_text_inline = True
    helper.help_text_inline = True
    helper.html5_required = True
    helper.layout = Layout(Fieldset('', 'tola_user_uuid', 'title', 'name', 'employee_number', 'user',
                                    'country', 'countries'),
                           Submit('submit', 'Submit', css_class='btn-default'),
                           Reset('reset', 'Reset', css_class='btn-warning'))


class NewUserRegistrationForm(UserCreationForm):
    """
    Form for registering a new account.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

    def __init__(self, *args, **kwargs):
        super(NewUserRegistrationForm, self).__init__(*args, **kwargs)

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-6'
    helper.form_error_title = 'Form Errors'
    helper.error_text_inline = True
    helper.help_text_inline = True
    helper.html5_required = True
    helper.form_tag = False


class NewTolaUserRegistrationForm(forms.ModelForm):
    """
    Form for registering a new account.
    """
    class Meta:
        model = TolaUser
        fields = ['title', 'privacy_disclaimer_accepted']

    org = forms.CharField()

    def clean_org(self):
        try:
            org = Organization.objects.get(name=self.cleaned_data['org'])
        except Organization.DoesNotExist:
            raise forms.ValidationError("The Organization was not found.")
        else:
            return org

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset('', 'title', 'org',),
            Fieldset('',
                     HTML("""
                        <div id="iframe" class="mt-2">
                            <h6>Notice/Disclaimer:</h6>
                            <div class="privacy-policy">
                                {% if privacy_disclaimer %}
                                    {{ privacy_disclaimer }}
                                {% else %}
                                    {% include "registration/privacy_policy.html" %}
                                {% endif %}
                            </div>
                        </div>
                     """),
                     Div('privacy_disclaimer_accepted',
                         css_class="mt-2")),
        )

        super(NewTolaUserRegistrationForm, self).__init__(*args, **kwargs)

        # Set default organization for demo environment
        if settings.DEFAULT_ORG and os.getenv('APP_BRANCH') == DEMO_BRANCH:
            self.fields['org'] = forms.CharField(
                initial=settings.DEFAULT_ORG, disabled=True)

        self.fields['privacy_disclaimer_accepted'].required = True


class BookmarkForm(forms.ModelForm):
    """
    Form for registering a new account.
    """
    class Meta:
        model = TolaBookmarks
        fields = ['name', 'bookmark_url']

    def __init__(self, *args, **kwargs):
        super(BookmarkForm, self).__init__(*args, **kwargs)

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-6'
    helper.form_error_title = 'Form Errors'
    helper.error_text_inline = True
    helper.help_text_inline = True
    helper.html5_required = True
    helper.form_tag = True
    helper.layout = Layout(
        Fieldset('','name','bookmark_url'),
        Submit('submit', 'Submit', css_class='btn-default'),
        Reset('reset', 'Reset', css_class='btn-warning'))


