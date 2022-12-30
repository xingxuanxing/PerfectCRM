from queenadmin.base_admin import BaseQueenAdmin

class AdminSite(object):
    def __init__(self):
        #能启用的admin {'crm':{'customer':CustomerAdmin,'role':RoleAdmin},'student':{'test':TestAdmmin}}
        self.enabled_admin={}


    def register(self,model_class,admin_class=None):

        app_name=model_class._meta.app_label
        model_name=model_class._meta.model_name
        #最后一次注册表的时候，覆盖了之前的admin_class.model。因为共享了同一块BaseQueenAdmin类内存.解决办法，实例化。

        if not admin_class:
            admin_class=BaseQueenAdmin()
        else:
            admin_class=admin_class()

        admin_class.model= model_class
        if not self.enabled_admin:
            self.enabled_admin[app_name]={}
        self.enabled_admin[app_name][model_name]=admin_class


site = AdminSite()