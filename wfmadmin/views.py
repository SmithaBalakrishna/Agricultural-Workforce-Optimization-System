from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from wfmadmin.models import *
from datetime import datetime
from django.http import HttpResponseNotAllowed
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect

# Create your views here.
def adminloginpage(request):
    return render(request, 'adminloginpage.html')

def adminloginaction(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('adminhome')
            else:
                return render(request, 'adminloginpage.html', {'error': True})
        else:
            return render(request, 'adminloginpage.html', {'error': True})
    else:
        return render(request, 'adminloginpage.html', {'error': True})
    
def adminlogout(request):
    return render(request, 'adminloginpage.html')

def adminhome(request):
    worker_count = worker.objects.count()
    customer_count = customer.objects.count()
    active_worker_count = worker.objects.filter(status=True).count()
    inactive_worker_count = worker.objects.filter(status=False).count()
    active_customer_count = customer.objects.filter(status=True).count()
    inactive_customer_count = customer.objects.filter(status=False).count()
    available_workers_count = WorkerProfile.objects.filter(status="Available").count()
    unavailable_workers_count = WorkerProfile.objects.filter(status="Unavailable").count()

    context = {
        'worker_count': worker_count,
        'customer_count': customer_count,
        'active_worker_count': active_worker_count,
        'inactive_worker_count': inactive_worker_count,
        'active_customer_count': active_customer_count,
        'inactive_customer_count': inactive_customer_count,
        'available_workers_count': available_workers_count,
        'unavailable_workers_count': unavailable_workers_count,
    }
    return render(request, 'admin/adminhome.html', context)

def admincustomerviews(request):
    customers = customer.objects.all().order_by('-created_at')
    return render(request, 'admin/admincustomerviews.html', {'registered_users': customers})

def adminworkerviews(request):
    workers = worker.objects.all().order_by('-created_at')
    return render(request, 'admin/adminworkerviews.html', {'registered_users': workers})

def AdminActiveworkers(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        print(id)
        worker.objects.filter(email=id).update(status=True)
        registered_users = worker.objects.all().order_by('-created_at')
        return render(request, "admin/adminworkerviews.html", {'registered_users': registered_users})
    
def AdmindeActiveworkers(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        print(id)
        worker.objects.filter(email=id).update(status=False)
        registered_users = worker.objects.all().order_by('-created_at')
        return render(request, "admin/adminworkerviews.html", {'registered_users': registered_users})
    
def AdminActivecustomers(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        print(id)
        customer.objects.filter(email=id).update(status=True)
        registered_users = customer.objects.all().order_by('-created_at')
        return render(request, 'admin/admincustomerviews.html', {'registered_users': registered_users})
    
def AdmindeActivecustomers(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        print(id)
        customer.objects.filter(email=id).update(status=False)
        registered_users = customer.objects.all().order_by('-created_at')
        return render(request, 'admin/admincustomerviews.html', {'registered_users': registered_users})
    
def adminviewrequestedservice(request):
    cus_req = CustomerServiceRequest.objects.filter(status = 'none',ser_status=True).exclude(pri_status__in=['priority']).order_by('-created_at')
    return render(request, 'admin/adminviewrequestedservice.html', {'customer_request': cus_req})

def update_service_request_status(request):
    pk = request.POST.get('pk')
    action = request.POST.get('action')

    service_request = get_object_or_404(CustomerServiceRequest, pk=pk)
    if action == 'accept':
        service_request.status = 'accepted'
    elif action == 'reject':
        service_request.status = 'rejected'

    service_request.save()

    return redirect('adminviewrequestedservice')

def adminviewassignedtasks(request):
    search_query = request.GET.get('search', '')
    if search_query:
        workers = worker.objects.filter(
            Q(firstname__icontains=search_query) |
            Q(lastname__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(number__icontains=search_query) |
            Q(workerprofile__profession__icontains=search_query) |
            Q(workerprofile__skills__icontains=search_query)
        ).filter(workerprofile__status='Available').order_by('-created_at')
    else:
        workers = worker.objects.filter(workerprofile__status='Available').order_by('-created_at')
    
    context = {
        'workers': workers
    }
    return render(request, 'admin/adminviewassignedtasks.html', context)

def admin_worker_details(request):
    worker_id = request.GET.get('id')
    worker_details = get_object_or_404(worker, id=worker_id)
    worker_profile = get_object_or_404(WorkerProfile, worker=worker_details)
    worker_skills = [skill.strip() for skill in worker_profile.skills.split(',')]
    skill_queries = Q()

    for skill in worker_skills:
        skill_queries |= Q(service__icontains=skill)

    assigned_requests = Assignment.objects.values_list('request_id', flat=True)
    matching_customer_requests = CustomerServiceRequest.objects.filter(
        skill_queries,
        status='accepted'
    ).exclude(id__in=assigned_requests).order_by('-created_at')

    assignments = Assignment.objects.filter(worker=worker_details)
    events = []
    for assignment in assignments:
        events.append({
            'title': assignment.title,
            'start': assignment.start.isoformat(),
            'end': assignment.end.isoformat()
        })

    context = {
        'worker': worker_details,
        'customer_request': matching_customer_requests,
        'events': events
    }
    return render(request, 'admin/admin_worker_details.html', context)

def assign_worker(request):
    if request.method == 'POST':
        worker_id = request.POST.get('worker_id')
        request_id = request.POST.get('request_id')

        worker_instance = get_object_or_404(worker, id=worker_id)
        selected_request = get_object_or_404(CustomerServiceRequest, id=request_id)
        selected_customer = get_object_or_404(customer, id=selected_request.user_id)

        start_datetime = datetime.combine(selected_request.start_date, selected_request.start_time)
        end_datetime = datetime.combine(selected_request.end_date, selected_request.end_time)

        assignment = Assignment.objects.create(
            worker=worker_instance,
            customer=selected_customer,
            request=selected_request,
            title=f"Service: {selected_request.service}",
            start=start_datetime,
            end=end_datetime
        )
        assignment.save()
        return redirect('adminviewassignedtasks')
    return HttpResponseNotAllowed(['POST'])

def monitortaskprogress(request):
    skills = request.GET.getlist('skills')
    if skills:
        query = Q()
        for skill in skills:
            query |= Q(request__service__icontains=skill)
        requeststatus = Assignment.objects.filter(query).order_by('-created_at')
    else:
        requeststatus = Assignment.objects.all().order_by('-created_at')

    payment_requests = PaymentRequest.objects.values_list('assignment_id', flat=True)
    
    return render(request, 'admin/monitortaskprogress.html', {'requeststatus': requeststatus, 'payment_requests': payment_requests})

def timeoffrequests(request):
    requeststatus = WorkerTimeOffRequest.objects.all().order_by('-requested_at')
    return render(request, 'admin/timeoffrequests.html', {'requeststatus': requeststatus})

def update_status(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_status = request.POST.get('status')
        user_request = WorkerTimeOffRequest.objects.get(id=user_id)
        user_request.status = new_status
        user_request.save()
        return redirect('timeoffrequests')

def adminpaymentrequest(request):
    requeststatus = PaymentRequest.objects.all().order_by('-created_at')
    return render(request, 'admin/adminpaymentrequest.html', {'requeststatus': requeststatus})

def adminviewcustomerfeedback(request):
    customer_request =UserFeedback.objects.all().order_by('-submitted_at')
    return render(request, 'admin/adminviewcustomerfeedback.html', {'customer_request': customer_request})

def adminpriorityrequest(request):
    cus_req = CustomerServiceRequest.objects.filter(status = 'none',ser_status=True, pri_status='priority').order_by('-created_at')
    return render(request, 'admin/adminpriorityrequest.html', {'customer_request': cus_req})

def admincustomersupport(request):
    customer_request =CustomerQuery.objects.all().order_by('-submitted_at')
    return render(request, 'admin/admincustomersupport.html', {'customer_request': customer_request})

@login_required
def adminworkersupport(request):
    customer_request =WorkerQuery.objects.all().order_by('-submitted_at')
    return render(request, 'admin/adminworkersupport.html', {'customer_request': customer_request})

def adminviewacceptedrequests(request):
    customer_request = CustomerServiceRequest.objects.filter(status = 'accepted').order_by('-created_at')
    return render(request, 'admin/adminviewacceptedrequests.html', {'customer_request': customer_request})

@csrf_protect
def request_payment(request):
    assignment_id = request.GET.get('assignment_id')
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.method == 'POST':
        service_charge = request.POST.get('service_charge')
        cgst = request.POST.get('cgst')
        sgst = request.POST.get('sgst')
        total_amount = request.POST.get('total_amount')

        PaymentRequest.objects.create(
            assignment=assignment,
            service_charge=service_charge,
            cgst=cgst,
            sgst=sgst,
            total_amount=total_amount
        )
        return redirect('adminpaymentrequest')  

    return render(request, 'admin/requestpayment.html', {'assignment': assignment})