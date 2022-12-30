from django.forms import ModelForm
from django import forms

class BaseForm(ModelForm):

    class Meta:
        readonly_fields = []


    def __new__(cls,*args,**kwargs):

        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs.update({'class':"form-control"})

            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs.update({'disabled':'true'})

        return ModelForm.__new__(cls)

    def clean(self):
        if self.errors:
            raise forms.ValidationError('Plese fix errors first!')
        # raise forms.ValidationError('Plese fix errors first!')
        if self.instance.id is not None:
            for field in self.Meta.readonly_fields:
                db_value= getattr(self.instance,field)
                user_value= self.cleaned_data.get(field)
                if db_value!=user_value:
                    self.add_error(field,'readonly filed 不允许修改,值应该是%s' %db_value)