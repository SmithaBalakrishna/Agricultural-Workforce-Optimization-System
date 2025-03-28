from django.urls import path
from .views import *

urlpatterns = [
    path('adminloginpage', adminloginpage, name='adminloginpage'),
    path('adminloginaction', adminloginaction, name='adminloginaction'),
    path('adminlogout', adminlogout, name='adminlogout'),
    path('adminhome', adminhome, name='adminhome'),
    path('admincustomerviews', admincustomerviews, name='admincustomerviews'),
    path('adminworkerviews', adminworkerviews, name='adminworkerviews'),
    path('AdmindeActiveworkers', AdmindeActiveworkers, name='AdmindeActiveworkers'),
    path('AdminActiveworkers', AdminActiveworkers, name='AdminActiveworkers'),
    path('AdmindeActivecustomers', AdmindeActivecustomers, name='AdmindeActivecustomers'),
    path('AdminActivecustomers', AdminActivecustomers, name='AdminActivecustomers'),
    path('adminviewrequestedservice', adminviewrequestedservice, name='adminviewrequestedservice'),
    path('adminviewassignedtasks', adminviewassignedtasks, name='adminviewassignedtasks'),
    path('monitortaskprogress', monitortaskprogress, name='monitortaskprogress'),
    path('adminpriorityrequest', adminpriorityrequest, name='adminpriorityrequest'),
    path('adminworkersupport', adminworkersupport, name='adminworkersupport'),
    path('timeoffrequests', timeoffrequests, name='timeoffrequests'),
    path('adminpaymentrequest', adminpaymentrequest, name='adminpaymentrequest'),
    path('adminviewcustomerfeedback', adminviewcustomerfeedback, name='adminviewcustomerfeedback'),
    path('admincustomersupport', admincustomersupport, name='admincustomersupport'),
    path('update_service_request_status', update_service_request_status, name='update_service_request_status'),
    path('admin_worker_details', admin_worker_details, name='admin_worker_details'),
    path('assign_worker', assign_worker, name='assign_worker'), 
    path('adminviewacceptedrequests', adminviewacceptedrequests, name='adminviewacceptedrequests'),
    path('update_status', update_status, name='update_status'),
    path('requestpayment', request_payment, name='requestpayment'),
    

]