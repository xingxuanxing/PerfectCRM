from django.test import TestCase

# Create your tests here.
class A():
    def __init__(self,x):
        self.x=x

    def add(self):
        return 3

a1= A(12)
res=a1.x
print(res)