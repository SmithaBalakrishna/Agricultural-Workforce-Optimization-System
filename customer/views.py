from django.shortcuts import render, redirect, get_object_or_404
from wfmadmin.models import *
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json
# Create your views here.

def customerloginpage(request):
    return render(request,'customerloginpage.html')

def customerregistrationaction(request):
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
        form1 = customer(firstname=firstname,lastname=lastname,address=address,city=city,state=state,country=country,username=username, email=email, number=number, password=password)
        form1.save()
        return render(request,'customerloginpage.html', {'success': True})
    else:
        return render(request,'customerloginpage.html', {'error': True})
    
def customerloginaction(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            customer_obj = customer.objects.get(email=email, password=password, status=True)
        except customer.DoesNotExist:
            return render(request, 'customerloginpage.html', {'error': True})
        request.session['customer_id'] = customer_obj.id
        request.session['customer_username'] = customer_obj.username
        return redirect('customerprofile')
    else:
        return render(request, 'customerloginpage.html', {'error': True})
    
def customerlogout(request):
    return render(request,'customerloginpage.html')
    
def customerprofile(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customerloginpage')
    try:
        customer_obj = customer.objects.get(id=customer_id)
    except customer.DoesNotExist:
        return redirect('customerloginpage')
    
    context = {
        'customer': customer_obj,
    }
    return render(request, 'customer/customerhome.html', context)

def update_customer_profile(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customerloginpage')
    try:
        customer_obj = customer.objects.get(id=customer_id)
    except customer.DoesNotExist:
        return redirect('customerloginpage')
    
    if request.method == 'POST':
        if 'firstname' in request.POST and request.POST['firstname']:
            customer_obj.firstname = request.POST['firstname']
        if 'lastname' in request.POST and request.POST['lastname']:
            customer_obj.lastname = request.POST['lastname']
        if 'address' in request.POST and request.POST['address']:
            customer_obj.address = request.POST['address']
        if 'city' in request.POST and request.POST['city']:
            customer_obj.city = request.POST['city']
        if 'state' in request.POST and request.POST['state']:
            customer_obj.state = request.POST['state']
        if 'country' in request.POST and request.POST['country']:
            customer_obj.country = request.POST['country']
        if 'username' in request.POST and request.POST['username']:
            customer_obj.username = request.POST['username']
        if 'email' in request.POST and request.POST['email']:
            customer_obj.email = request.POST['email']
        if 'number' in request.POST and request.POST['number']:
            customer_obj.number = request.POST['number']

        customer_obj.save()
        return redirect('customerprofile')
    else:
        return redirect('customerprofile')
    
def update_customer_profile_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('oldpassword')
        new_password = request.POST.get('newpassword')
        cfrm_password = request.POST.get('confirm_password')

        customer_id = request.session.get('customer_id')
        current_customer = customer.objects.get(id=customer_id)

        if old_password != current_customer.password:
            messages.error(request, "Old password is incorrect.")
            return redirect('customerprofile')  

        if new_password != cfrm_password:
            messages.error(request, "New password and confirm password do not match.")
            return redirect('customerprofile') 
         
        current_customer.password = new_password
        current_customer.save()
        messages.success(request, "Password updated successfully.")
        return redirect('customerprofile') 
    return redirect('customerprofile') 

def createservicerequest(request):
    return render(request, 'customer/createservicerequest.html')

def createservicerequest_action(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        fulladdress = request.POST.get('fulladdress')
        location = request.POST.get('location')
        services = request.POST.getlist('service[]')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        user_id = request.session.get('customer_id')

        services_str = ', '.join(services)

        new_request = CustomerServiceRequest(
            user_id = user_id,
            fullname=fullname,
            fulladdress=fulladdress,
            location=location,
            service=services_str,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time
        )
        new_request.save()
        messages.success(request, 'Service request created successfully.')
        return redirect('createservicerequest')
    else:
        messages.success(request, 'Service request created Un-successfull.')
        return redirect('createservicerequest')

def trackservicerequest(request):
    user_id = request.session.get('customer_id')
    cus_requests = CustomerServiceRequest.objects.filter(user_id = user_id, ser_status = True).order_by('-created_at')
    return render(request, 'customer/trackservicerequest.html', {'customer_request': cus_requests})

def set_priority(request):
    pk = request.GET.get('pk')
    if pk:
        service_request = get_object_or_404(CustomerServiceRequest, pk=pk)
        service_request.pri_status = 'priority'
        service_request.save()
    return redirect('trackservicerequest')

def delete_service_request(request):
    if request.method == 'GET':
        pk = request.GET.get('pk')
        if pk:
            service_request = get_object_or_404(CustomerServiceRequest, pk=pk)
            service_request.ser_status = False
            service_request.save()
            return redirect('trackservicerequest') 
    return redirect('trackservicerequest')

def assignedworkers(request):
    user_id = request.session.get('customer_id')
    customer_request = Assignment.objects.filter(customer=user_id, status__in=['none', 'incomplete']).order_by('-created_at')
    return render(request, 'customer/assignedworkers.html', {'customer_request': customer_request})

def chat_interface(request):
    assignment_id = request.GET.get('request_id')
    assignment = get_object_or_404(Assignment, id=assignment_id)
    messages = ChatMessage.objects.filter(assignment=assignment).order_by('timestamp')
    context = {
        'assignment': assignment,
        'messages': messages,
        'user': customer.objects.get(id=request.session.get('customer_id'))
    }
    return render(request, 'customer/chat_interface.html', context)

@csrf_exempt
@login_required
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        assignment_id = data.get('assignment_id')
        message_text = data.get('message')
        
        assignment = get_object_or_404(Assignment, id=assignment_id)
        sender = customer.objects.get(id=request.session.get('customer_id'))
        recipient = assignment.worker
        
        message = ChatMessage.objects.create(
            assignment=assignment,
            customer_sender=sender,
            message=message_text
        )
        
        return JsonResponse({
            'sender': message.customer_sender.username,
            'message': message.message,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

def rate_review_workers(request):
    user_id = request.session.get('customer_id')
    completed_assignments = Assignment.objects.filter(customer=user_id,status='complete')
    workers = [assignment.worker.username for assignment in completed_assignments]
    customer_request = Userratereview.objects.filter(user=user_id)
    return render(request, 'customer/rate_review_workers.html', {'workers': workers, 'customer_request': customer_request})

@login_required
def submit_rating_review(request):
    if request.method == 'POST':
        worker_username = request.POST['worker']
        rating = request.POST['rating']
        review = request.POST['review']
        
        user_id = request.session.get('customer_id')
        user = customer.objects.get(id=user_id)
        
        worker_id = worker.objects.get(username=worker_username)
        
        user_feedback = Userratereview(user=user, worker=worker_id, rating=rating, review=review)
        user_feedback.save()

    return redirect('rate_review_workers')

def userpayment(request):
    user_id = request.session.get('customer_id')
    if user_id:
        requeststatus = PaymentRequest.objects.filter(assignment__customer_id=user_id)
    else:
        requeststatus = PaymentRequest.objects.none()  
    return render(request, 'customer/userpayment.html', {'requeststatus': requeststatus})

def payment_gateway(request):
    if request.method == 'POST':
        payment_request_id = request.POST.get('payment_request_id')
        payment_request = get_object_or_404(PaymentRequest, id=payment_request_id)
        utr_number = request.POST.get('utr_number')
        screenshot = request.FILES.get('screenshot')

        payment_detail = PaymentDetail(
            payment_request=payment_request,
            utr_number=utr_number,
            screenshot=screenshot
        )
        payment_detail.save()

        payment_request.status = 'completed'
        payment_request.save()

        return redirect('userpayment')

    else:
        payment_request_id = request.GET.get('payment_request_id')
        payment_request = get_object_or_404(PaymentRequest, id=payment_request_id)
        return render(request, 'customer/payment_gateway.html', {'payment_request': payment_request})

def userservicehistory(request):
    user_id = request.session.get('customer_id')
    customer_request = Assignment.objects.filter(customer=user_id, status__in=['complete']).order_by('-created_at')
    return render(request, 'customer/userservicehistory.html', {'customer_request': customer_request})

def userfeedback(request):
    if request.method == 'POST':
        rating = request.POST['rating']
        comments = request.POST['comments']
        user_id = request.session.get('customer_id')
        user = customer.objects.get(id=user_id)
        user_feedback = UserFeedback(user=user, rating=rating, comments=comments)
        user_feedback.save()
    return render(request, 'customer/userfeedback.html')


def customersupport(request):
    user_id = request.session.get('customer_id')
    customer_request =CustomerQuery.objects.filter(user=user_id)
    return render(request, 'customer/customersupport.html', {'customer_request': customer_request})

def customer_support_action(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        query = request.POST['query']
        
        user_id = request.session.get('customer_id')
        user = customer.objects.get(id=user_id)
        
        customer_query = CustomerQuery(user=user, name=name, email=email, query=query)
        customer_query.save()
    return redirect('customersupport')

def customercancledservicerequest(request):
    user_id = request.session.get('customer_id')
    cus_requests = CustomerServiceRequest.objects.filter(user_id = user_id, ser_status = False).order_by('-created_at')
    return render(request, 'customer/customercancledservicerequest.html', {'customer_request': cus_requests})