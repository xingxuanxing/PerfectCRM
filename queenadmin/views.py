from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
import json
from queenadmin.app_setup import queenadmin_autodiscover_app
from queenadmin.sites import site
from queenadmin.form_handle import dynamic_create_modelform
from queenadmin.permissions import check_permission

queenadmin_autodiscover_app()

@check_permission
@login_required
def app_index(request):
    from crm.models import UserProfile
    print(request.user,request)
    return render(request,'queenadmin/app_index.html',{'site':site})

def get_filtered_result(request,query_set,admin_class):
    filter_condition={}
    print(request.GET)
    for k,v in request.GET.items():
        if k in ('_o','_page') :continue

        if v:
            if k == 'date':
                filter_condition['date__gte'] = v
            elif k =='_q':
                search_keyword=request.GET.get('_q')
                q=Q()
                q.connector='OR'
                for search_field in admin_class.search_fields:
                    q.children.append(('%s__contains' %search_field, search_keyword))
                print(q)
                query_set = query_set.filter(q)

            else:
                filter_condition[k]=v
    query_set = query_set.filter(**filter_condition)

    filter_condition['date'] = filter_condition.pop('date__gte','')
    print(filter_condition)

    return query_set,filter_condition

def get_sorted_result(request,query_set,admin_class):
    sorted_index=request.GET.get('_o')
    sorted_dict={}   #{'name':'-0'}
    #如果排序了
    if sorted_index:
        sorted_filed=admin_class.list_display[abs(int(sorted_index))]
        sorted_dict[sorted_filed]=sorted_index
        if sorted_index.startswith('-'):
            sorted_filed='-'+sorted_filed
        return query_set.order_by(sorted_filed),sorted_dict
    else:
        return query_set,sorted_dict

@check_permission
@login_required
def table_obj_list(request,app_name,model_name):
    admin_class =site.enabled_admin[app_name][model_name]

    if request.method=='POST':
        action = request.POST.get('action')
        chosen_ids = json.loads(request.POST.get('chosen_ids'))
        if not action: #如果不是action行为的post请求，那就是一个删除操作

            chosen_objs = admin_class.model.objects.filter(id__in=chosen_ids)
            chosen_objs.delete()
        else: #如果是action,执行action里定义的方法。

            chosen_objs = admin_class.model.objects.filter(id__in=chosen_ids)
            admin_class_func = getattr(admin_class, action)
            response = admin_class_func(request, chosen_objs)
            if response:
                return response


    query_set=admin_class.model.objects.all().order_by('-id')

    query_set,filter_condition=get_filtered_result(request,query_set,admin_class)
    admin_class.filter_condition=filter_condition
    admin_class.search_keyword=request.GET.get('_q','')

    #先过滤，再排序，最后是分页.....现在是排序调用
    query_set,sorted_dict =get_sorted_result(request,query_set,admin_class)


    paginator = Paginator(query_set, admin_class.list_per_page)  # Show 2 contacts per page.
    page_number = request.GET.get('_page')
    query_set = paginator.get_page(page_number)

    return render(request,'queenadmin/table_obj_list.html',{'query_set':query_set,
                                                            'admin_class':admin_class,
                                                            'sorted_dict':sorted_dict,
                                                            'app_name':app_name,
                                                            'model_name':model_name,
                                                            })

@check_permission
@login_required
def table_obj_change(request,app_name,model_name,nid):
    admin_class=site.enabled_admin[app_name][model_name]
    model_form=dynamic_create_modelform(admin_class)
    obj=admin_class.model.objects.filter(id=nid).first()
    if request.method=='GET':
        form_obj=model_form(instance=obj)
    elif request.method=='POST':
        form_obj=model_form(instance=obj,data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('/queenadmin/%s/%s/' %(app_name,model_name))   #('(\w+)/(\w+)/$',views.table_obj_list,name='table-obj-list'),
    return render(request,'queenadmin/table_obj_change.html',locals())


@check_permission
@login_required
def table_obj_delete(request,app_name,model_name,nid):
    admin_class = site.enabled_admin[app_name][model_name]
    delete_obj= admin_class.model.objects.filter(id=nid).first()
    if request.method=='POST':
        delete_obj.delete()
        return redirect('/queenadmin/%s/%s/' %(app_name,model_name))
    return render(request,'queenadmin/table_obj_delete.html',locals())


@check_permission
@login_required
def table_obj_add(request,app_name,model_name):
    admin_class = site.enabled_admin[app_name][model_name]
    model_form = dynamic_create_modelform(admin_class,form_add=True)

    if request.method == 'GET':
        form_obj = model_form()
    elif request.method == 'POST':
        form_obj = model_form(data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('/queenadmin/%s/%s/' % (app_name, model_name))

    return render(request,'queenadmin/table_obj_add.html',locals())



def acc_login(request):
    error_msg=''
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(username=username,password=password)
        print(username,password,user)
        if user:
            login(request,user)
            return redirect(request.GET.get('next','/queenadmin/'))
        else:
            error_msg='wrong username or password'

    return render(request,'queenadmin/login.html',{'error_msg':error_msg})

def acc_logout(request):
    logout(request)
    return redirect('/queenadmin/login/')


