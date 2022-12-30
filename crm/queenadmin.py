from queenadmin.sites import site
from crm import models
from queenadmin.base_admin import BaseQueenAdmin


class CustomerAdmin(BaseQueenAdmin):
    list_display = ['name','source','contact_type','contact','consultant','consult_content','status','date']
    list_filter = ['source','consultant','status','date']
    search_fields = ['name','consult_content','consultant__name']
    readonly_fields = ['status','contact']
    filter_horizontal = ['consult_courses',]
    actions = ['change_status', ]

    def change_status(self, request, querysets):
        print('actions:23444')
        querysets.update(status=1)

class StudentAdmin(BaseQueenAdmin):
    filter_horizontal = ['class_grades', ]

class UserProfileAdmin(BaseQueenAdmin):
    filter_horizontal = ['role', ]

#在admin网页上注册app的 表

site.register(models.Student)
site.register(models.ClassGrade)
site.register(models.CustomerFollowUp)
site.register(models.CustomerInfo,CustomerAdmin)
site.register(models.CourseRecord)
site.register(models.StudyRecord)
site.register(models.Branch)
site.register(models.Course)
site.register(models.Menus)
site.register(models.Role)
site.register(models.ContractTemplate)
site.register(models.Entrollment)
site.register(models.Student,StudentAdmin)
site.register(models.UserProfile,UserProfileAdmin)
