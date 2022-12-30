from django.shortcuts import render,redirect
from django.urls import resolve
from django.conf import settings
from queenadmin.permission_list import perm_dic

def perm_check(*args,**kwargs):
    request=args[0]
    resolve_url_obj= resolve(request.path)
    current_url_name= resolve_url_obj.url_name

    if request.user.is_authenticated is False: #验证用户是否登录
        return redirect(settings.LOGIN_URL)

    match_results= [None,]
    match_key= None
    for permission_key,permission_val in perm_dic.items():
        perm_url_name = permission_val[0]
        perm_method = permission_val[1]
        perm_args = permission_val[2]
        perm_kwagrs = permission_val[3]
        perm_hook_func= permission_val[4] if len(permission_val)>4 else None

        if perm_url_name == current_url_name:
            if perm_method == request.method:
                # args_matched = False
                for item in perm_args:
                    request_method_func= getattr(request,perm_method) #request.POST/GET
                    if request_method_func.get(item,None):
                        args_matched = True
                    else:
                        args_matched = False
                        break #匹配perm_dic中【】里的参数，若遇到匹配不上，直接退出循环
                else:
                    args_matched = True

                # kwargs_matched= False #匹配有特定值的参数
                for k,v in perm_kwagrs.items():
                    request_method_func= getattr(request,perm_method)
                    arg_val= request_method_func.get(k,None) #用户请求中有这个参数
                    if arg_val == str(v):
                        kwargs_matched= True
                    else:
                        kwargs_matched= False
                        break
                else:
                    kwargs_matched= True


                # perm_hook_matched= False
                if perm_hook_func:
                    perm_hook_matched= perm_hook_func(request)
                else:
                    perm_hook_matched= True


                match_results = [args_matched, kwargs_matched,perm_hook_matched]
                if all(match_results):
                    match_key = permission_key
                    break

    if all(match_results):
        app_name,per_name= match_key.split('_',1)
        perm_obj='%s.%s' %(app_name,match_key)
        if request.user.has_perm(perm_obj):
            print('当前用户有此权限')
            return True
        else:
            print('当前用户没有该权限')
            return False

    else:
        print('未匹配到权限项，当前用户无权限')
        return False





def check_permission(func):
    def inner(*args,**kwargs):
        if not perm_check(*args,**kwargs):
            request = args[0]
            return render(request,'queenadmin/page_403.html')
        return func(*args,**kwargs)
    return inner