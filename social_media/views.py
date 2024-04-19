from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, auth
from django.contrib import messages 
from .models import Profile
from django.contrib.auth.decorators import login_required


@login_required(login_url='signin')
def index(request):
  return render(request, 'index.html')

@login_required(login_url='signin')
def settings(request):
  return render(request, 'settings.html')


def signup(request):
  if request.method == 'POST':
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    password2 = request.POST['password2']
    if password == password2:
      if User.objects.filter(email=email).exists():
        messages.info(request, "Email already taken")
        return redirect('signup')
      
      elif User.objects.filter(username=username).exists():
        messages.info(request, "Username already taken")
        return redirect('signup')
      else:
        user = User.objects.create_user(
            username=username, email=email, password=password)
        user.save()
        
        # log user in and redirect to settings page
        user_login = auth.authenticate(username=username, password=password)
        auth.login(request, user_login)
        
        # create a user profile object for the new user
        user_model = User.objects.get(username=username)
        new_profile = Profile.objects.create(user=user_model, id_user = user_model.id, username = user_model.username)
        new_profile.save()
        return redirect('settings')
    else:
      messages.info(request, "Password Not same")
      redirect('signup')
      
    # user = authenticate(request, username=username, password=password)
    # if user.is_valid:

    return render(request, 'signup.html')
  else: 
    return render(request, 'signup.html')
  
  
def signin(request):
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']
    user = auth.authenticate(username = username, password = password)
    if user is not None:
      auth.login(request, user)
      return redirect('/')
    else:
      messages.info(request, "User credentials not correct, please try again.")
      return redirect('/signin')
  else:
    return render(request, 'signin.html')


@login_required(login_url='signin')  
def logout(request):
  auth.logout(request)
  messages.info(request, "You have been logged out successfully")
  
  return redirect('/signin')
  