from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginForm
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
        
    context = {
        'form': form,
    }
    
    return render(request, 'accounts/signup.html', context)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('webtoon_list')
    else:
        form = LoginForm()
        
    context = {
        'form': form,
    }
    
    return render(request, 'accounts/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('accounts:login')
