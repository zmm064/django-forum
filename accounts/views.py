from django.shortcuts import render, redirect
from django.contrib.auth import login

from .forms import SignUpForm

def signup(request):
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')
    return render(request, 'signup.html', {'form': form})
