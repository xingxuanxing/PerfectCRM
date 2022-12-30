

def view_myown_customers(request):
    print('permission hook func is  running')
    if str(request.user.id) == request.GET.get('consultant'):
        print('登录的人可以查看自己销售咨询的客户信息')
        return True
    else:
        return False