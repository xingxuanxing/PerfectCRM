from django.forms import ModelForm


def dynamic_create_modelform(admin_class,form_add=False):
    """
    动态生成form表单，当 form_add为True时，新增表单，反之，为修改的表单
    """
    class Meta:
        model=admin_class.model
        fields="__all__"
        if not form_add:#如果构造的是 修改的表单，form表单排除掉可读的字段，前端单独创建p标签。
            exclude=admin_class.readonly_fields
        #     admin_class.form_add=form_add
        # else: #添加表单
        #     admin_class.form_add=form_add
        admin_class.form_add=form_add

    #在生成动态表单的时候，执行__init__方法前调用new方法对其字段对象进行属性调整
    def __new__(cls,*args,**kwargs):
        print(cls.base_fields)
        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs.update({'class':"form-control"})

        return ModelForm.__new__(cls)


    model_form=type('DynamicForm',(ModelForm,),{'Meta':Meta,'__new__':__new__})

    return model_form