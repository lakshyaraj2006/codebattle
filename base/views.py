from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from .forms import CustomUserCreationForm, SubmissionForm, UserCreationForm
from .models import User, Event, Submission
# Create your views here.

def login_page(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

    page = 'login'
    context = {'page': page}
    return render(request, "login_register.html", context)

def logout_user(request):
    logout(request)
    return redirect('login')

def register_page(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    page = 'register'
    context = {'page': page, 'form': form}
    return render(request, "login_register.html", context)

def index(request):
    users = User.objects.filter(hackathon_participant=True).all()
    events = Event.objects.filter().all()
    context = {'users': users, 'events': events}
    return render(request, "home.html", context)

def event_page(request, pk):
    event = get_object_or_404(Event, id=pk)
    submitted = False
    
    if request.user.is_authenticated:
        submitted = Submission.objects.filter(event=event, participant=request.user).exists()

    context = {'event': event, 'submitted': submitted}
    return render(request, "event.html", context)

def user_page(request, pk):
    user = get_object_or_404(User, id=pk)
    context = {'user': user}
    return render(request, "profile.html", context)

@login_required(login_url='/login/')
def account_page(request):
    user = request.user
    context = {'user': user}
    return render(request, "account.html", context)

def register_confirmation(request, pk):
    event = get_object_or_404(Event, id=pk)

    if request.method == "POST":
        event.participants.add(request.user)
        return redirect('event', pk=pk)

    context = {'event': event}
    return render(request, "event_confirmation.html", context)

@login_required(login_url='/login/')
def project_submission(request, pk):
    event = get_object_or_404(Event, id=pk)

    if request.user not in event.participants.all():
        return redirect("event", pk=pk)

    submitted = Submission.objects.filter(event=event, participant=request.user).exists()
    if submitted:
        return redirect("event", pk=pk)

    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.event = event
            submission.participant = request.user
            submission.save()

            return redirect("event", pk=pk)
        
        return redirect("event", pk=pk)
    else:
        form = SubmissionForm()

    context = {'event': event, 'form': form}
    return render(request, "submit_form.html", context)

# Add owner authentication
@login_required(login_url='/login/')
def update_submission(request, pk):
    submission = get_object_or_404(Submission, id=pk)

    if request.user != submission.participant:
        return HttpResponse("You cannot edit this submission!!!")

    event = submission.event

    if request.method == "POST":
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.event = event
            submission.participant = request.user
            submission.save()

            return redirect("account")
        
        return redirect("account")
    else:
        form = SubmissionForm(instance=submission)

    context = {'form': form, 'event': event}
    return render(request, "submit_form.html", context)
