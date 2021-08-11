from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.index,name='blogindex'),
    path('blogpost/<int:id>',views.blogpost,name='blogpost')
]