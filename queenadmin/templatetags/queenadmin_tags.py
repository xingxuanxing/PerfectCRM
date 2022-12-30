from django.template import Library
from django.utils.safestring import mark_safe
import datetime,time

register=Library()

@register.simple_tag
def build_filter_field(filter_field,admin_class):
    filter_ele = '<div class="col-md-2">%s:<select class="form-control" name=%s>' %(filter_field, filter_field)
    filter_field_obj = admin_class.model._meta.get_field(filter_field)
    # print(filter_field_obj)
    try:
        for choice in filter_field_obj.get_choices(): #过滤的字段，有choices的字段 和FK字段,都可以使用get_choices()方法--字段对象
            selected=''
            #存在该过滤条件，在url上，该字段的choice被选中
            if str(choice[0]) == admin_class.filter_condition.get(filter_field):
                selected='selected'
            option= '<option %s value=%s>%s</option>' %(selected,*choice)

            filter_ele+=option

    except AttributeError as e:
        # print(filter_field_obj.get_internal_type())
        if filter_field_obj.get_internal_type() in ('DateField','DateTimeField'):
            ctime=datetime.datetime.now()
            timelist=[
                ('','-------'),
                (ctime,'Today'),
                (ctime-datetime.timedelta(7),'七天之内'),
                (ctime.replace(day=1),'本月'),
                (ctime-datetime.timedelta(90),'三个月内'),
                (ctime.replace(month=1,day=1),'本年'),
            ]

            for time_ in timelist:
                selected=''
                # '' if not time_[0] else time_[0].strftime('%Y-%m-%d')
                if (('%s' % time_[0]).split(' ')[0])==admin_class.filter_condition.get(filter_field):
                    selected='selected'
                option='<option %s value=%s>%s</option>' %(selected,*time_)
                filter_ele+=option

    filter_ele+='</select></div>'
    return mark_safe(filter_ele)

@register.simple_tag
def build_table_row(obj,admin_class):

    ele=''
    if admin_class.list_display:
        for index,column in enumerate(admin_class.list_display):
            #取出每个字段对象。接着判断该字段是否是choice字段。
            column_obj = obj._meta.get_field(column)

            if column_obj.choices:
                column_text=getattr(obj,'get_%s_display' %column)()
            else: # foreignkey的字段
                column_text=getattr(obj,column)

            td_ele='<td>%s</td>' %column_text
            if index==0:
                td_ele='<td><a href="%s/change">%s</a></td>' %(obj.id,column_text)
            ele+=td_ele
    else:
        td_ele='<td><a href="%s/change">%s</a></td>' %(obj.id,obj)
        ele+=td_ele

    return mark_safe(ele)

@register.simple_tag
def get_model_name(admin_class):
    return admin_class.model._meta.model_name.upper()

@register.simple_tag
def get_field_value(form_obj, field):
    if form_obj.instance._meta.get_field(field).choices:
        field_value=getattr(form_obj.instance,"get_%s_display" %field)()
    else:
        field_value= getattr(form_obj.instance,field)
    return field_value


@register.simple_tag
def get_sorted_index(sorted_dict):#获取已排序的字段的索引
    if sorted_dict:
        return list(sorted_dict.values())[0]
    return ''



@register.simple_tag
def get_sort_index(forloop,sorted_dict,column):#通过上一次排序后，得到下一次排序的索引 ?_o=-0
    if column in sorted_dict: #排序过
        sorted_index=sorted_dict[column]
        if sorted_index.startswith('-'):
            next_sort_index=sorted_index.strip('-')
        else:
            next_sort_index='-%s' %sorted_index
        return next_sort_index
    else:#没有排序过，就直接获取这个字段的索引即前端list_display的循环次数
        return forloop

@register.simple_tag
def generate_sorted_arrow(column,sorted_dict):
    if column in sorted_dict:
        arrow_direction='top'
        if sorted_dict[column].startswith('-') :
            arrow_direction='bottom'
        ele='<span class="glyphicon glyphicon-triangle-%s" aria-hidden="true"></span>' %arrow_direction
        return mark_safe(ele)
    else:
        return ''

@register.simple_tag
def get_filter_args(admin_class):
    ele=''
    if admin_class.search_keyword:
        ele='&%s=%s'%('_q',admin_class.search_keyword)
    if admin_class.filter_condition:
        for k,v in admin_class.filter_condition.items():
            ele+='&%s=%s'%(k,v)

    return mark_safe(ele)




@register.simple_tag
def render_pagenation_btn(query_set,admin_class,sorted_dict):
    ele="<ul class='pagination'>"
    filter_args =get_filter_args(admin_class)
    sorted_index=get_sorted_index(sorted_dict)

    disabled = 'disabled'
    pre=1 #当第一页的时候不可点<<

    if query_set.has_previous():
        pre=query_set.previous_page_number()
        disabled=''
    ele+='<li class=%s> <a href="?_page=%s&_o=%s%s">&laquo;</a></li>' % (disabled,pre,sorted_index,filter_args)

    for btn in query_set.paginator.page_range:

        if abs(btn-query_set.number)<3 : #display btn
            active=''
            if btn==query_set.number: #current_page
                active='active'
            per_btn_ele='<li class=%s > <a href="?_page=%s&_o=%s%s"> %s </a></li>' %(active,btn,sorted_index,filter_args,btn)
            ele += per_btn_ele

    disabled = 'disabled'
    nex = query_set.paginator.num_pages  # 当下一页是最后一页的时候不可点>>
    if query_set.has_next():
        disabled=''
        nex=query_set.next_page_number()

    ele+='<li class=%s> <a href="?_page=%s&_o=%s%s">&raquo;</a></li>' %(disabled,nex,sorted_index,filter_args)

    ele+='</ul>'

    return mark_safe(ele)


@register.simple_tag
def get_available_datas(admin_class,form_obj,field_name):
    field_obj = admin_class.model._meta.get_field(field_name)
    gross_set = set(field_obj.related_model.objects.all())
    if not admin_class.form_add:

        chosen_set= set(get_chosen_datas(admin_class,form_obj,field_name))
        return gross_set - chosen_set
    else:
        return gross_set




@register.simple_tag
def get_chosen_datas(admin_class,form_obj, field_name):
    """
    该数据关联的多对多字段值
    """
    if not admin_class.form_add:
        chosen_queryset =getattr(form_obj.instance,field_name).all()
        return chosen_queryset
    else:
        return []

@register.simple_tag
def display_related_data(delete_obj):
    ele='<ul>'


    for related_table in delete_obj._meta.related_objects:
        related_table_name =related_table.name
        # ele += '<li>%s<ul>' % related_table_name
        related_objs =getattr(delete_obj,'%s_set' % related_table_name).all() #反向查所有关联的数据
        if related_table.get_internal_type()=='ManyToManyField':
            for i in related_objs:
                ele+='<li>影响%s中(<a href="/queenadmin/%s/%s/%s/change">%s</a>)数据的相关信息</li>' \
                     %(related_table_name,i._meta.app_label,i._meta.model_name,i.id,i)
        else:#与外键相关的表
            for i in related_objs:
                ele+='<li>删除%s:<a href="/queenadmin/%s/%s/%s/change">%s</a></li>'\
                     %(i._meta.model_name,i._meta.app_label,i._meta.model_name,i.id,i)
                ele+=display_related_data(i)

        # ele+='</ul></li>'

    ele+='</ul>'

    return ele