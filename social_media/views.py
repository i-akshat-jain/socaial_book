from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, auth
from django.contrib import messages 
from .models import Profile, Post, LikePost, FollowersCount
from django.contrib.auth.decorators import login_required
from itertools import chain


@login_required(login_url='signin')
def index(request):
  user_object = User.objects.get(username=request.user.username)
  user_profile = Profile.objects.get(user=user_object)
  
  user_following_list = []
  feed = []
  
  user_following = FollowersCount.objects.filter(follower = request.user.username)
  
  for users in user_following:
    user_following_list.append(users.user)
  
  for usernames in user_following_list:
    feed_list = Post.objects.filter(user=usernames)
    feed.append(feed_list)
  
  feed_list = list(chain(*feed))
  posts = Post.objects.all()
  return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_list})

@login_required(login_url='signin')
def settings(request):
  user_profile = Profile.objects.get(user=request.user)
  
  if request.method == 'POST':
    if 'image' in request.FILES:
        image = request.FILES['image'].read()  # Read the binary image data
        user_profile.profileimg = image
    else:
        image = request.POST.get('profileimg', '') 
        
    bio = request.POST.get('bio', '')
    location = request.POST.get('location', '')
    
    user_profile.bio = bio
    user_profile.location = location
    user_profile.save()
    
    return redirect('settings')
  return render(request, 'settings.html', {'user_profile': user_profile})



@login_required(login_url='signin')
def upload(request):
  if request.method == 'POST':
    
    user_profile = Profile.objects.get(user=request.user)
    user = request.user.username
    image = request.FILES['image_upload'].read()
    caption = request.POST.get('caption')
    
    new_post = Post.objects.create(
        user=user, user_profile=user_profile, image=image, caption=caption)
    new_post.save()
    return redirect('/')

  else:
    return redirect('/')


@login_required(login_url='signin')
def like_post(request):
  username = request.user.username
  post_id = request.GET.get('post_id')
  
  post = Post.objects.get(id=post_id)
  like_filter = LikePost.objects.filter(post_id = post_id, username=username).first()
  if like_filter == None:
    new_like = LikePost.objects.create(username=username, post_id=post_id)
    new_like.save()
    post.no_of_likes += 1
    post.save()
    return redirect('/') 
  else:
    like_filter.delete()
    post.no_of_likes -= 1
    post.save()
    return redirect('/') 


@login_required(login_url='signin')
def profile(request, pk):
  user_object = User.objects.get(username=pk)
  user_profile = Profile.objects.get(user=user_object)
  user_posts = Post.objects.filter(user=pk)
  user_post_length = len(user_posts)
  
  follower = request.user.username
  user = pk
  
  if FollowersCount.objects.filter(follower=follower, user=user).first():
      button_text = 'Unfollow'
  else:
      button_text = 'Follow'
      
  user_followers = len(FollowersCount.objects.filter(user=pk))
  user_following = len(FollowersCount.objects.filter(follower=pk))
  
  context = {
      'user_object': user_object,
      'user_profile': user_profile,
      'user_posts': user_posts,
      'user_post_length': user_post_length,
      'button_text': button_text,
      'user_followers': user_followers,
      'user_following': user_following,
  }
  return render(request, 'profile.html', context)

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        
        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})


@login_required(login_url='signin')  
def follow(request):
  if request.method == 'POST':
    follower = request.POST['follower']
    user = request.POST['user']
    
    if FollowersCount.objects.filter(follower=follower, user=user).first():
      delete_follower = FollowersCount.objects.get(follower=follower, user=user)
      delete_follower.delete()
      return redirect('/profile/'+user)
    else:
      new_follower = FollowersCount.objects.create(follower=follower, user=user)
      new_follower.save()
      return redirect('/profile/'+user)
  else:
    return redirect('/')

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
  