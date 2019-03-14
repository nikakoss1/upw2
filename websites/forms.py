# -*- coding: utf-8 -*-
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, ButtonHolder, Submit, Field
from django import forms
from .dubicars_models import Update, Website


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Update
        fields = ['status',]

    def __init__(self, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(

            )
        self.fields['status'].widget = forms.HiddenInput()
