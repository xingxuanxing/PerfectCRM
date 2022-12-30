from django.shortcuts import render

class BaseQueenAdmin:
    def __init__(self):
        # print(self)
        #判断adminclass是基类的对象，就先清空actions，不然基类下面的actions开辟了一个内存空间，固定的。注册model的时候，实例化的基类调用actions，
        #一直给actions指向的内存地址追加default_actions。
        if type(self) == BaseQueenAdmin:
            self.actions =[]
        self.actions.extend(self.defalut_actions)

        #如果用的是基类的action，注册一开始，是空数组，就一直把基类的action置为空数组。其他自定义的adminclass的action有值，不满足条件，不用置空
        # if not self.actions:
        #     self.actions=[]
        # self.actions.extend(self.defalut_actions)


    list_display=[]
    list_filter=[]
    search_fields=[]
    readonly_fields=[]
    filter_horizontal=[]
    list_per_page=10
    defalut_actions=['delete_datas',]
    actions=[]


    def delete_datas(self,request,querysets):#querryset是请求传进来的选择的数据
        print('fffsfs')
        chosen_ids=[]
        for obj in querysets:
            chosen_ids.append(obj.id)


        return render(request,'queenadmin/table_obj_delete.html',{'admin_class':self,
                                                                  'delete_objs':querysets,
                                                                  'chosen_ids':chosen_ids})

