from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Bienvenue sur le forum !")
            return redirect('forum:thread-list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
