from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class customer(models.Model):
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    email = models.EmailField(max_length=20)
    number = models.IntegerField()
    password = models.CharField(max_length=20)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class CustomerServiceRequest(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    fullname = models.CharField(max_length=100)
    fulladdress = models.CharField(max_length=255)
    location = models.CharField(max_length=1024)
    service = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=100, default='none')
    pri_status = models.CharField(max_length=100, default='none')
    ser_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fullname
    
class worker(models.Model):
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    email = models.EmailField(max_length=20)
    number = models.IntegerField()
    password = models.CharField(max_length=20)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class WorkerProfile(models.Model):
    worker = models.OneToOneField(worker, on_delete=models.CASCADE)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], blank=True)
    profession = models.CharField(max_length=50, blank=True)
    skills = models.TextField(blank=True)
    experience = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, default="Unavailable")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.worker.username}'s Profile"

class Assignment(models.Model):
    id = models.AutoField(primary_key=True)
    worker = models.ForeignKey(worker, on_delete=models.CASCADE)
    customer = models.ForeignKey(customer, on_delete=models.CASCADE)
    request = models.ForeignKey(CustomerServiceRequest, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    start = models.DateTimeField()
    end = models.DateTimeField()
    status = models.CharField(max_length=100, default='none')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.worker.username} assigned to {self.customer.username} for {self.request.service}"

class WorkerTimeOffRequest(models.Model):
    id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    time_off_duration = models.CharField(max_length=20)
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"Time off request by {self.assignment.worker.username} for {self.time_off_duration}"
    
class ChatMessage(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    customer_sender = models.ForeignKey(customer, null=True, blank=True, on_delete=models.CASCADE, related_name='sent_messages')
    worker_sender = models.ForeignKey(worker, null=True, blank=True, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.customer_sender or self.worker_sender} at {self.timestamp}'
    
class WorkReport(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    worker = models.ForeignKey(worker, on_delete=models.CASCADE)
    report = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class CustomerQuery(models.Model):
    user = models.ForeignKey(customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    query = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query by {self.name} ({self.email})"
    
class WorkerQuery(models.Model):
    user = models.ForeignKey(worker, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    query = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query by {self.name} ({self.email})"
    
class UserFeedback(models.Model):
    user = models.ForeignKey(customer, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comments = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username} with rating {self.rating}"
    
class Userratereview(models.Model):
    user = models.ForeignKey(customer, on_delete=models.CASCADE)
    worker = models.ForeignKey(worker, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    review = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username} for {self.worker.username} with rating {self.rating}"
    
class PaymentRequest(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2)
    cgst = models.DecimalField(max_digits=10, decimal_places=2)
    sgst = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default='pending')


    def __str__(self):
        return f"Payment request for {self.assignment}"
    
class PaymentDetail(models.Model):
    payment_request = models.OneToOneField(PaymentRequest, on_delete=models.CASCADE)
    utr_number = models.CharField(max_length=100)
    screenshot = models.ImageField(upload_to='payment_screenshots/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment detail for {self.payment_request}"