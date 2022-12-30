from django.urls import path,re_path
from queenadmin import views

urlpatterns = [
    re_path('^$',views.app_index,name='app_index'),
    re_path('(\w+)/(\w+)/$',views.table_obj_list,name='table_obj_list'),
    re_path('(\w+)/(\w+)/(\d+)/change',views.table_obj_change,name='table_obj_change'),
    re_path('(\w+)/(\w+)/(\d+)/delete',views.table_obj_delete,name='table_obj_delete'),
    re_path('(\w+)/(\w+)/add', views.table_obj_add, name='table_obj_add'),
    path('login/',views.acc_login),
    path('logout/',views.acc_logout,name='logout'),

]



