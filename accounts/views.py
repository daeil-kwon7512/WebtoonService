from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # 저장된 user 객체를 반환받음
            # 회원가입 후 자동 로그인
            login(request, user)
            return redirect('toons:webtoon_list')
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
            return redirect('toons:webtoon_list')
    else:
        form = LoginForm()
        
    context = {
        'form': form,
    }
    return render(request, 'accounts/login.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')

@login_required
def signout_view(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        return redirect('accounts:signup')
    return render(request, 'accounts/signout.html')
