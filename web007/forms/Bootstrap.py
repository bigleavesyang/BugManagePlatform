from django import forms


class BootStrapMixin(forms.Form):
    bootstrap_class_exclude = []

    def add_bootstrap_class(self):
        for name, field in self.fields.items():
            if name in self.bootstrap_class_exclude:
                continue
            old_class = field.widget.attrs.get('class', "")
            field.widget.attrs['class'] = f'{old_class} form-control'
            field.widget.attrs['placeholder'] = f'请输入{field.label}'
