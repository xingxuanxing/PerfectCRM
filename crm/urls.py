
from django.urls import path,re_path
from crm import views

urlpatterns = [

    #动态菜单--即对应的url含有正则的情况，url的name:sales_dashboard
    path('',views.dashboard,name='sales_dashboard'),
    path('stu-entrollment/',views.stu_entrollment,name='stu_entrollment'),
    re_path('stu-entrollment/(\d+)/contract-audit/',views.contract_audit,name='contract_audit'),
    re_path('entrollment/(\d+)/',views.entrollment,name='entrollment'),
    re_path('entrollment/certificate_upload/(\d+)',views.entrollment_certificate_upload,name='certificate_upload'),

    path('login/',views.acc_login),
    path('logout/',views.acc_logout,name='logout'),

]
