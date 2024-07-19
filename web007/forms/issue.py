from django import forms
from web007.forms.Bootstrap import BootStrapMixin
from web007.models import Issue


class IssueForm(forms.ModelForm, BootStrapMixin):
    class Meta:
        model = Issue
        exclude = ['creator', 'project', 'create_time', 'last_update_time']
        widgets = {
            'assign': forms.Select(attrs={'class': 'selectpiker form-select', 'data-live-search': 'true'}),
            'attention': forms.SelectMultiple(attrs={
                'class': 'selectpiker form-select', 'data-live-search': 'true', 'data-actions-box': 'true'
            }),
            "parent": forms.Select(attrs={'class': "selectpicker form-select", "data-live-search": "true"}),
            'start_date': forms.DateInput(attrs={'autocomplete': 'false'}),
            'end_date': forms.DateInput(attrs={'autocomplete': 'false'}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'form-select'
        self.fields['priority'].widget.attrs['class'] = 'form-select'
        self.fields['issues_type'].widget.attrs['class'] = 'form-select'
        self.bootstrap_class_exclude = ['assign', 'attention', 'parent', 'status', 'priority']
        self.add_bootstrap_class()
