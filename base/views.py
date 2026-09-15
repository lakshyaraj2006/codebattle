from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, update_session_auth_hash
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages

from .decorators import is_guest
from .utils import get_favicon
from .forms import CustomAuthenticationForm, CustomPasswordChangeForm, CustomUserCreationForm, SubmissionForm, UserForm
from .models import User, Event, Submission
# Create your views here.

@is_guest("account")
def login_page(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("home")
    else:
        form = CustomAuthenticationForm()

    context = {
        "page": "login",
        "form": form,
    }
    return render(request, "login_register.html", context)

@login_required(login_url='/login/')
def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')

@is_guest("account")
def register_page(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    page = 'register'
    context = {'page': page, 'form': form}
    return render(request, "login_register.html", context)

def home_page(request):
    users = User.objects.filter(hackathon_participant=True)

    try:
        limit = int(request.GET.get("limit", 20))
    except (TypeError, ValueError):
        limit = 1

    limit = max(1, min(limit, 50))

    paginator = Paginator(users, limit)

    page_number = request.GET.get("page", 20)

    try:
        users_page = paginator.page(page_number)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)

    events = Event.objects.all()

    context = {
        "users": users_page,
        "events": events,
        "users_count": users.count(),
        "paginator": paginator,
        "limit": limit,
    }

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

    socials = [
        ("Twitter", user.twitter),
        ("LinkedIn", user.linkedin),
        ("Website", user.website),
        ("Facebook", user.facebook),
        ("GitHub", user.github),
    ]

    socials = [
        {
            "name": name,
            "url": url,
            "icon": get_favicon(url)
        }
        for name, url in socials
        if url
    ]

    context = {'user': user, 'socials': socials}
    return render(request, "profile.html", context)

@login_required(login_url='/login/')
def account_page(request):
    user = request.user
    context = {'user': user}
    return render(request, "account.html", context)

@login_required(login_url='/login/')
def edit_account(request):
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=request.user)
        avatar = request.user.avatar
        is_uploaded = request.FILES.get("avatar")

        if form.is_valid():
            user = form.save()
            if is_uploaded and avatar.name.startswith(f"avatars/{request.user.username}_"):
                avatar.delete(save=False)

            messages.success(request, "Account updated successfully!")
            return redirect("account")
    else:
        form = UserForm(instance=request.user)
    context = {'form': form}
    return render(request, "user_form.html", context)

@login_required(login_url='/login/')
def change_password(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            form.save()

            update_session_auth_hash(request, request.user)
            messages.success(request, "Password changed successfully!")
            return redirect("account")
    else:
        form = CustomPasswordChangeForm(request.user)
    context = {'form': form}
    return render(request, "change_password.html", context)

def register_confirmation(request, pk):
    event = get_object_or_404(Event, id=pk)

    if request.method == "POST":
        event.participants.add(request.user)
        messages.success(request, "Registered for event successfully!")
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

            messages.success(request, "Project submitted successfully!")
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

            messages.success(request, "Submission updated successfully!")
            return redirect("account")
        
        return redirect("account")
    else:
        form = SubmissionForm(instance=submission)

    context = {'form': form, 'event': event}
    return render(request, "submit_form.html", context)
