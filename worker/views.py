from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from wfmadmin.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json
from django.db.models import Exists, OuterRef
# Create your views here.

def workerloginpage(request):
    return render(request,'workerloginpage.html')

def workerregistrationaction(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        username = request.POST.get('username')
        email = request.POST.get('email')
        number = request.POST.get('phone')
        password = request.POST.get('password')
        form1 = worker(firstname=firstname,lastname=lastname,address=address,city=city,state=state,country=country,username=username, email=email, number=number, password=password)
        form1.save()
        return render(request, 'workerloginpage.html', {'success': True})
    else:
        return render(request, 'workerloginpage.html', {'error': True})

def workerloginaction(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            worker_obj = worker.objects.get(email=email, password=password, status=True)
        except worker.DoesNotExist:
            return render(request, 'workerloginpage.html', {'error': True})
        request.session['worker_id'] = worker_obj.id
        request.session['worker_username'] = worker_obj.username
        return redirect('workerprofile')
    else:
        return render(request, 'workerloginpage.html', {'error': True})

def workerlogout(request):
    return redirect('workerloginpage')

def workerprofile(request):
    worker_id = request.session.get('worker_id')
    if not worker_id:
        return redirect('workerloginpage')
    try:
        worker_obj = worker.objects.get(id=worker_id)
    except worker.DoesNotExist:
        return redirect('workerloginpage')
    worker_profile, created = WorkerProfile.objects.get_or_create(worker=worker_obj)
    
    context = {
        'worker': worker_obj,
        'worker_profile': worker_profile
    }
    return render(request, 'worker/workerhome.html', context)

def update_worker_profile(request):
    worker_id = request.session.get('worker_id')
    if not worker_id:
        return redirect('workerloginpage')
    try:
        worker_obj = worker.objects.get(id=worker_id)
    except worker.DoesNotExist:
        return redirect('workerloginpage')
    
    worker_profile, created = WorkerProfile.objects.get_or_create(worker=worker_obj)
    
    if request.method == 'POST':
        if 'firstname' in request.POST and request.POST['firstname']:
            worker_obj.firstname = request.POST['firstname']
        if 'lastname' in request.POST and request.POST['lastname']:
            worker_obj.lastname = request.POST['lastname']
        if 'address' in request.POST and request.POST['address']:
            worker_obj.address = request.POST['address']
        if 'city' in request.POST and request.POST['city']:
            worker_obj.city = request.POST['city']
        if 'state' in request.POST and request.POST['state']:
            worker_obj.state = request.POST['state']
        if 'country' in request.POST and request.POST['country']:
            worker_obj.country = request.POST['country']
        if 'username' in request.POST and request.POST['username']:
            worker_obj.username = request.POST['username']
        if 'email' in request.POST and request.POST['email']:
            worker_obj.email = request.POST['email']
        if 'number' in request.POST and request.POST['number']:
            worker_obj.number = request.POST['number']

        if 'age' in request.POST and request.POST['age']:
            worker_profile.age = request.POST['age']
        if 'gender' in request.POST and request.POST['gender']:
            worker_profile.gender = request.POST['gender']
        if 'profession' in request.POST and request.POST['profession']:
            worker_profile.profession = request.POST['profession']
        if 'skills[]' in request.POST:
            selected_skills = request.POST.getlist('skills[]')
            worker_profile.skills = ','.join(selected_skills)
        if 'experience' in request.POST and request.POST['experience']:
            worker_profile.experience = request.POST['experience']

        worker_obj.save()
        worker_profile.save()
        return redirect('workerprofile')
    else:
        return redirect('workerprofile')

def change_status(request):
    worker_id = request.GET.get('worker_id')
    new_status = request.GET.get('status')
    worker_profile = get_object_or_404(WorkerProfile, worker_id=worker_id)
    if new_status in ["Available", "Unavailable"]:
        worker_profile.status = new_status
        worker_profile.save()
    return redirect('workerprofile')

def update_worker_profile_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('oldpassword')
        new_password = request.POST.get('newpassword')
        cfrm_password = request.POST.get('confirm_password')

        worker_id = request.session.get('worker_id')
        current_worker = worker.objects.get(id=worker_id)

        if old_password != current_worker.password:
            messages.error(request, "Old password is incorrect.")
            return redirect('workerprofile')  

        if new_password != cfrm_password:
            messages.error(request, "New password and confirm password do not match.")
            return redirect('workerprofile') 
         
        current_worker.password = new_password
        current_worker.save()
        messages.success(request, "Password updated successfully.")
        return redirect('workerprofile') 
    return render(request, 'workerprofile')

def workerviewassignedtask(request):
    user_id = request.session.get('worker_id')
    customer_request = Assignment.objects.filter(worker = user_id).exclude(status='complete').order_by('-created_at')
    return render(request, 'worker/workerviewassignedtask.html', {'customer_request':customer_request})

def update_assignment_status(request):
    if request.method == "POST":
        req_id = request.POST.get('req_id')
        assignment = get_object_or_404(Assignment, id=req_id)
        status = request.POST.get('status')
        if status in ['complete', 'incomplete']:
            assignment.status = status
            assignment.save()
            messages.success(request, 'Assignment status updated successfully.')
        else:
            messages.error(request, 'Invalid status value.')
    return redirect('workerviewassignedtask')

def worker_request_time_off(request):
    if request.method == 'POST':
        req_id = request.POST.get('req_id')
        time_off_duration = request.POST.get('time_off_duration')
        assignment = get_object_or_404(Assignment, id=req_id)
        WorkerTimeOffRequest.objects.create(
            assignment=assignment,
            time_off_duration=time_off_duration,
            status='pending'
        )
        return redirect('workerviewassignedtask')

def worker_chat_interface(request):
    assignment_id = request.GET.get('request_id')
    assignment = get_object_or_404(Assignment, id=assignment_id)
    messages = ChatMessage.objects.filter(assignment=assignment).order_by('timestamp')
    context = {
        'assignment': assignment,
        'messages': messages,
        'user': worker.objects.get(id=request.session.get('worker_id'))
    }
    return render(request, 'worker/worker_chat_interface.html', context)

@csrf_exempt
@login_required
def worker_send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        assignment_id = data.get('assignment_id')
        message_text = data.get('message')
        
        assignment = get_object_or_404(Assignment, id=assignment_id)
        sender = worker.objects.get(id=request.session.get('worker_id'))
        recipient = assignment.customer
        
        message = ChatMessage.objects.create(
            assignment=assignment,
            worker_sender=sender,
            message=message_text
        )
        
        return JsonResponse({
            'sender': message.worker_sender.username,
            'message': message.message,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

def workercompletedtask(request):
    user_id = request.session.get('worker_id')
    completed_assignments = Assignment.objects.filter(worker=user_id, status='complete').order_by('-created_at')
    
    completed_assignments = completed_assignments.annotate(
        report_exists=Exists(WorkReport.objects.filter(assignment=OuterRef('pk')))
    )
    
    return render(request, 'worker/workercompletedtask.html', {'customer_request': completed_assignments})

def workerschedulemanagement(request):
    user_id = request.session.get('worker_id')
    customer_request = Assignment.objects.filter(worker = user_id, status='incomplete').order_by('-created_at')
    return render(request, 'worker/workerschedulemanagement.html', {'customer_request':customer_request})

def update_assignment(request):
    if request.method == 'POST':
        assignment_id = request.POST.get('assignment_id')
        start_date = request.POST.get('start')
        end_date = request.POST.get('end')

        assignment = get_object_or_404(Assignment, id=assignment_id)
        assignment.start = start_date
        assignment.end = end_date
        assignment.status = 'none'
        assignment.save()

        return redirect('workerschedulemanagement')
    
def workersubmitreport(request):
    if request.method == 'POST':
        user_id = request.session.get('worker_id')
        assignment_id = request.POST.get('assignment_id')
        report_content = request.POST.get('report')

        worker_instance = get_object_or_404(worker, id=user_id)
        
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        work_report = WorkReport.objects.create(
            assignment=assignment,
            worker=worker_instance, 
            report=report_content
        )
        return redirect('workercompletedtask')  
    
    assignment_id = request.GET.get('assignment_id')
    assignment = get_object_or_404(Assignment, id=assignment_id)
    return render(request, 'worker/workersubmitreport.html', {'assignment': assignment})

def workerearnings(request):
    user_id = request.session.get('worker_id')
    if user_id:
        requeststatus = PaymentRequest.objects.filter(assignment__worker_id=user_id)
    else:
        requeststatus = PaymentRequest.objects.none()
    return render(request, 'worker/workerearnings.html', {'requeststatus': requeststatus})

def workercustomersupport(request):
    worker_id = request.session.get('worker_id')
    customer_request =WorkerQuery.objects.filter(user=worker_id)
    return render(request, 'worker/workercustomersupport.html', {'customer_request': customer_request})

def worker_support_action(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        query = request.POST['query']
        
        user_id = request.session.get('worker_id')
        user = worker.objects.get(id=user_id)
        
        customer_query = WorkerQuery(user=user, name=name, email=email, query=query)
        customer_query.save()
    return redirect('workercustomersupport')