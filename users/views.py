from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # connexion directe après inscription
            return redirect('home')  # tu peux changer la redirection
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users\login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

from projects.models import Project, Task

@login_required
def home_view(request):
    user = request.user
    projects = Project.objects.filter(owner=user)
    tasks = Task.objects.filter(assigned_to=user)
    return render(request, 'users/home.html', {'user': user, 'projects': projects, 'tasks': tasks})

