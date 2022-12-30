from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,PermissionsMixin
)


class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_superuser  = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,

    )
    name=models.CharField(max_length=64,verbose_name="姓名")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.ManyToManyField('Role', blank=True)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    class Meta:
        permissions=(
            ('crm_app_index','可以允许所有app里的表',),
            ('crm_table_list', '可以查看每张表里的数据',),
            ('crm_table_change_view', '可以查看数据的修改页',),
            ('crm_table_list_change', '可以对数据进行修改',),
            ('crm_table_obj_add_view', '可以查看添加页',),
            ('crm_table_obj_add', '可以对数据进行添加',),
        )

# class UserProfile(models.Model):
#     """用户信息表:销售人员，讲师，课程顾问等用户"""
#     user=models.OneToOneField(User,on_delete=models.CASCADE)
#     name=models.CharField(max_length=64,verbose_name="姓名")
#
#     #WARNINGS:crm.UserProfile.role: (fields.W340) null has no effect on ManyToManyField.
#     role=models.ManyToManyField('Role',blank=True)
#
#     def __str__(self):
#         return self.name

class Role(models.Model):
    """角色表"""
    name= models.CharField(max_length=64,unique=True)
    menus=models.ManyToManyField('Menus',blank=True)

    def __str__(self):
        return self.name

class CustomerInfo(models.Model):
    """客户信息表"""
    name = models.CharField(max_length=64,default=None)

    contact_type_choices=((0,'qq'),(1,'email'),(2,'phone'))
    contact_type = models.SmallIntegerField(choices=contact_type_choices,default=0)  #两个字节，16bit
    contact = models.CharField(max_length=64,unique=True)

    source_choices=((0,'qq群'),(1,'51CTO'),(2,'百度推广'),(3,'知乎'),(4,'转介绍'),(5,'其他'))
    source = models.SmallIntegerField(choices=source_choices)
    referral_from = models.ForeignKey('self',blank=True,null=True,verbose_name="介绍人",on_delete=models.CASCADE)

    consult_courses=models.ManyToManyField('Course',verbose_name='咨询课程')
    consult_content= models.TextField(verbose_name="咨询内容")

    status_choices=((0,'未报名'),(1,'已报名'),(2,'已退学'))
    status = models.SmallIntegerField(choices=status_choices)
    consultant= models.ForeignKey('UserProfile',verbose_name="课程顾问",on_delete=models.CASCADE)

    id_num= models.CharField(max_length=64,blank=True,null=True)
    sex_choices=((0,'男'),(1,'女'))
    sex= models.SmallIntegerField(choices=sex_choices,blank=True,null=True)
    emergency_contact= models.CharField(max_length=64,blank=True,null=True)

    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

class CustomerFollowUp(models.Model):
    """客户跟踪记录表"""
    customer=models.ForeignKey('CustomerInfo',on_delete=models.CASCADE)
    content=models.TextField(verbose_name='跟踪内容')
    follower= models.ForeignKey('UserProfile',verbose_name="跟进人",on_delete=models.CASCADE)
    status_choices=((0,'近期无报名计划'),(1,'一个月内报名'),(2,'2周内报名'),(3,'已报名'))
    status=models.SmallIntegerField(choices=status_choices)
    date= models.DateField(auto_now_add=True)

    def __str__(self):
        return self.content

class Course(models.Model):
    """课程表:python，linux"""
    name=models.CharField(max_length=64,unique=True,verbose_name='课程名称')
    price=models.PositiveSmallIntegerField()
    period = models.PositiveSmallIntegerField(verbose_name='课程周期(月)',default=5)
    outline = models.TextField(verbose_name='大纲')

    def __str__(self):
        return self.name

class ClassGrade(models.Model):
    """班级表：一个班级只能报一种课程学习"""
    branch = models.ForeignKey('Branch',on_delete=models.CASCADE)
    class_type_choices=((0,'脱产'),(1,'周末'),(2,'网络'))
    class_type=models.SmallIntegerField(choices=class_type_choices)
    course = models.ForeignKey('Course',on_delete=models.CASCADE)
    semester= models.PositiveSmallIntegerField(verbose_name="学期")
    contract_template= models.ForeignKey('ContractTemplate',on_delete=models.CASCADE)
    teachers = models.ManyToManyField('UserProfile',verbose_name='讲师')
    start_date= models.DateField("开班日期")
    graduate_date=models.DateField('毕业日期',blank=True,null=True)

    #联合唯一
    class Meta:
        unique_together=('course','semester','class_type')

    def __str__(self):
        return '%s(%s)期 %s' %(self.course,self.semester,self.class_type)


class CourseRecord(models.Model):
    """上课记录"""
    class_grade=models.ForeignKey('ClassGrade',verbose_name='上课班级',on_delete=models.CASCADE)
    day_num= models.PositiveSmallIntegerField(verbose_name='课程节次')
    teacher= models.ForeignKey('UserProfile',on_delete=models.CASCADE)
    title = models.CharField('本节主题',max_length=64)
    content=models.TextField('本节内容')
    has_homework = models.BooleanField('本节作业',default=True)
    homework= models.TextField('作业内容',blank=True,null=True)
    date=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=('class_grade','day_num')

    def __str__(self):
        return "%s第(%s)节" %(self.class_grade,self.day_num)

class Student(models.Model):
    """学员表"""
    customer=models.OneToOneField('CustomerInfo',on_delete=models.CASCADE)
    class_grades =models.ManyToManyField('ClassGrade')

    def __str__(self):
        return "%s" %self.customer


class StudyRecord(models.Model):
     """学习记录：学生的一节课程的作业成绩和考勤"""
     course_record=models.ForeignKey('CourseRecord',on_delete=models.CASCADE)
     student =models.ForeignKey('Student',on_delete=models.CASCADE)
     attend_choices=(
         (0,'缺勤'),(1,'已签到'),(2,'迟到'),(3,'早退'),
     )
     attend_status=models.SmallIntegerField(choices=attend_choices,default=1)

     score_choices=(
         (100,'A+'),(90,'A'),(85,'B'),(80,'B-'),(70,'C'),(-50,'D'),(0,'N/A'),
                    )
     score=models.SmallIntegerField(choices=score_choices,default=0)
     note= models.TextField('成绩备注',blank=True,null=True)
     date=models.DateTimeField(auto_now_add=True)

     def __str__(self):
         return "%s-%s-%s" %(self.course_record,self.student,self.score)


class Branch(models.Model):
    """校区"""
    name = models.CharField(max_length=64,unique=True)
    addr= models.CharField(max_length=128,blank=True,null=True)

    def __str__(self):
        return self.name

class Menus(models.Model):
    """动态菜单"""
    name= models.CharField(max_length=64)
    url_type_choices=((0,'absolute'),(1,'dynamic'))
    url_type=models.SmallIntegerField(choices=url_type_choices)
    url=models.CharField(max_length=128)

    class Meta:
        unique_together=('name','url')

    def __str__(self):
        return '%s %s' %(self.name,self.url)

class ContractTemplate(models.Model):
    name = models.CharField(max_length=64)
    content = models.TextField()

    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

class Entrollment(models.Model):
    customer= models.ForeignKey('CustomerInfo',on_delete=models.CASCADE)
    classgrade= models.ForeignKey('ClassGrade',on_delete=models.CASCADE)
    consultant = models.ForeignKey('UserProfile',on_delete=models.CASCADE)
    contract_signed=models.BooleanField(default=False)
    contract_signed_date=models.DateTimeField(blank=True,null=True)
    contract_approved= models.BooleanField(default=False)
    contract_approved_date=models.DateTimeField(verbose_name='合同审核时间',blank=True,null=True)

    class Meta:
        unique_together=('customer','classgrade')

    def __str__(self):
        return '%s的报名表' %self.customer

class PaymentRecord(models.Model):
    entrollment= models.ForeignKey('Entrollment',on_delete=models.CASCADE)
    payment_type_choices=((0,'报名费'),(1,'学费'),(2,'退费'))
    payment_type = models.SmallIntegerField(choices=payment_type_choices,default=0)
    payment_amount= models.IntegerField('费用',default=500)

    date= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s-%s' %(self.payment_amount,self.entrollment)

