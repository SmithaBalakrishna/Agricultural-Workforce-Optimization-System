from django.urls import path
from .views import *

urlpatterns = [
    path('workerloginpage', workerloginpage,name='workerloginpage'),
    path('workerrregistrationaction', workerregistrationaction, name='workerregistrationaction'),
    path('workerloginaction', workerloginaction, name='workerloginaction'),
    path('workerlogout', workerlogout, name='workerlogout'),
    path('workerprofile', workerprofile, name='workerprofile'),
    path('update_worker_profile', update_worker_profile, name='update_worker_profile'),
    path('change_status', change_status, name='change_status'),
    path('update_worker_profile_password', update_worker_profile_password, name='update_worker_profile_password'),
    path('workerviewassignedtask', workerviewassignedtask, name='workerviewassignedtask'),
    path('update-assignment-status/', update_assignment_status, name='update_assignment_status'),
    path('worker_request_time_off', worker_request_time_off, name='worker_request_time_off'),
    path('worker_chat_interface', worker_chat_interface, name='worker_chat_interface'),
    path('worker_send_message', worker_send_message, name='worker_send_message'),
    path('workercompletedtask', workercompletedtask, name='workercompletedtask'),
    path('workerschedulemanagement', workerschedulemanagement, name='workerschedulemanagement'),
    path('update_assignment', update_assignment, name='update_assignment'),
    path('workersubmitreport', workersubmitreport, name='workersubmitreport'),
    path('workerearnings', workerearnings, name='workerearnings'),
    path('workercustomersupport', workercustomersupport, name='workercustomersupport'),
    path('worker_support_action', worker_support_action, name='worker_support_action'),
]