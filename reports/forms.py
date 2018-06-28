from django.core.urlresolvers import reverse_lazy

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

from .models import *
from workflow.models import Country, WorkflowLevel1, Sector
from functools import partial

class DatePicker(forms.DateInput):
    """
    Use in form to create a Jquery datepicker element
    """
    template_name = 'dateslider.html'

    DateInput = partial(forms.DateInput, {'class': 'slider'})


class FilterForm(forms.Form):

    country = forms.ModelChoiceField(
        queryset = Country.objects.all(),
        required = False,
        empty_label = None,
        widget = forms.SelectMultiple(),
    )
    workflowlevel1 = forms.ModelChoiceField(
        queryset = WorkflowLevel1.objects.all(),
        required = False,
        empty_label = None,
        widget = forms.SelectMultiple(),
    )
    sector = forms.ModelChoiceField(
        queryset = Sector.objects.all(),
        required = False,
        empty_label = None,
        widget = forms.SelectMultiple(),
    )
    start_date = forms.DateField(widget=DatePicker.DateInput(), required=False)
    end_date = forms.DateField(widget=DatePicker.DateInput(), required=False)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class='form-horizontal'
        self.helper.html5_required = True
        self.helper.form_id = "filter_form"
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            # set custom id for country becasue of javascript reuse of default id
            Field('country', css_class="input-sm", id="countries"),
            Field('workflowlevel1', css_class="input-sm"),
            Field('sector', css_class='input-sm'),
            #Field('start_date', css_class='input-sm'),
            #Field('end_date', css_class='input-sm'),

        )
        self.helper.form_method = 'get'
        self.helper.form_action = '/reports/report/'
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-sm'))
        self.helper.add_input(Reset('reset', 'Reset', css_id='id_search_form_reset_btn', css_class='btn-warning btn-sm'))
        super(FilterForm, self).__init__(*args, **kwargs)
