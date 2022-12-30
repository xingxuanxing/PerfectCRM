import datetime
import json
import os.path
#练习git
from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators import csrf
from django import conf
from django.db.utils import IntegrityError
from django.utils import timezone
from crm import models,form

def acc_login(request):
    error_msg=''
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(username=username,password=password)
        print(username,password,user)
        if user:
            login(request,user)
            return redirect(request.GET.get('next','/'))
        else:
            error_msg='wrong username or password'

    return render(request,'login.html',{'error_msg':error_msg})

def acc_logout(request):
    logout(request)
    return redirect('/crm/login/')

@login_required
def dashboard(request):

    return render(request,'crm/dashboard.html')

@login_required
def stu_entrollment(request):
    customers = models.CustomerInfo.objects.all()
    classgrades = models.ClassGrade.objects.all()
    if request.method == 'POST':
        customer_id= request.POST.get('customer')
        classgrade_id= request.POST.get('classgrade')
        try:
            entrollment_obj=models.Entrollment.objects.create(
                customer_id=customer_id,
                classgrade_id=classgrade_id,
                consultant=request.user.userprofile
            )
            entrollment_link='http://localhost:8000/crm/entrollment/%s' %(entrollment_obj.id)
        except IntegrityError as e: #已存在报名表
            entrollment_obj= models.Entrollment.objects.get(customer_id=customer_id,
                classgrade_id=classgrade_id,)
            if entrollment_obj:
                return redirect('/crm/stu-entrollment/%s/contract-audit/' %entrollment_obj.id)


    return render(request,'crm/stu_entrollment.html',locals())

def contract_audit(request,entrollment_id):

    entrollment_obj= models.Entrollment.objects.get(id=entrollment_id)
    customer_form = form.CustomerForm(instance=entrollment_obj.customer)

    if request.method == 'POST':
        print(request.POST)
        entrollment_form=form.EntrollmentForm(instance=entrollment_obj,data=request.POST)
        if entrollment_form.is_valid():
            entrollment_form.save()
            stu_obj= models.Student.objects.get_or_create(customer=entrollment_obj.customer)[0]
            stu_obj.class_grades.add(entrollment_obj.classgrade_id)
            stu_obj.save()
            #审核时间
            entrollment_obj.customer.status=1
            entrollment_obj.customer.save()
            entrollment_obj.contract_approved_date=datetime.datetime.now()
            entrollment_obj.save()


            return redirect('/queenadmin/crm/customerinfo/%s/change' %entrollment_obj.customer.id)

    else:
        entrollment_form = form.EntrollmentForm(instance=entrollment_obj)


    return render(request,'crm/contract_audit.html',locals())




def entrollment(request,entrollment_id):

    entrollment_obj= models.Entrollment.objects.filter(id=entrollment_id).first()

    if entrollment_obj.contract_signed:
        return HttpResponse('合同正在审核中，请等待')

    if request.method=='POST':
        print(request.POST)
        customer_form = form.CustomerForm(instance=entrollment_obj.customer,data=request.POST)
        if customer_form.is_valid():
            customer_form.save()
            entrollment_obj.contract_signed= True
            entrollment_obj.contract_signed_date=timezone.now()
            entrollment_obj.save()

            return HttpResponse('报名成功，请等待顾问审核')

    else:
        customer_form = form.CustomerForm(instance=entrollment_obj.customer)

    #列出已上传的文件
    uploaded_files =[]
    entrollment_upload_dir = os.path.join(conf.settings.CRM_ENTROLLMENT_DATA_DIR, entrollment_id)
    if os.path.isdir(entrollment_upload_dir):
        uploaded_files = os.listdir(entrollment_upload_dir)

    return render(request,'crm/entrollment.html',locals())

@csrf.csrf_exempt
def entrollment_certificate_upload(request,entrollment_id):
    print(request.FILES)
    print(conf.settings.CRM_ENTROLLMENT_DATA_DIR)
    #每个学员上传的证件资料分别放在一个目录
    entrollment_upload_dir=os.path.join(conf.settings.CRM_ENTROLLMENT_DATA_DIR,entrollment_id)
    if not os.path.isdir(entrollment_upload_dir):
        os.mkdir(entrollment_upload_dir)

    file_obj=request.FILES.get('file')
    if len(os.listdir(entrollment_upload_dir))<2:
        #打开文件，要写东西进去
        with open(os.path.join(entrollment_upload_dir,file_obj.name),'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
    else:
        return HttpResponse(json.dumps({'status':False,'error_msg':'max upload limit is 2'}))



    return HttpResponse(json.dumps({'status':True}))