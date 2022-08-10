from itertools import chain
from random import shuffle, sample

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required


from .models import Profile, Post, LikePost, FollowersCount


# Create your views here.

 
User = get_user_model()

@login_required
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    feed = []
    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for user in user_following:
        feed_list = Post.objects.filter(user=user)
        feed.append(feed_list)
    
    posts = list(chain(*feed))

    all_profiles = Profile.objects.all()
    user_following_all = []

    for user in user_following:
        user_following_all.append(Profile.objects.get(user__username=user.user))

    current_user_profile = Profile.objects.get(user=request.user)
    suggestions = list(filter(lambda x: x not in list(user_following_all) and x != current_user_profile, all_profiles))

    shuffle(suggestions)
    final_suggestions = sample(suggestions, 2)


    context = {
        'user_profile': user_profile,
        'posts': posts,
        'final_suggestions': final_suggestions,
    }
    return render(request, 'index.html', context)


@login_required
def search(request):
    # user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(id_user=request.user.id)
    if request.method == 'POST':
        username = request.POST.get('username')
        username_objects = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for user in username_objects:
            username_profile.append(Profile.objects.filter(user=user))
        
        username_profile_list = list(chain(*username_profile))
        context = {
            'user_profile': user_profile,
            'username_profile_list': username_profile_list
        }

        return render(request, 'search.html', context)
    else:
        return redirect('/')


@login_required
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        caption = request.POST.get('caption')
        image = request.FILES.get('image_upload')

        post = Post.objects.create(user=user, caption=caption, image=image)
        messages.info(request, 'image is successfully uploaded!!')
        return redirect('/')

    else:
        messages.info(request, 'image upload is failed!!')
        return redirect('/')


@login_required
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    if LikePost.objects.filter(post_id=post_id, username=username).exists():
        LikePost.objects.get(post_id=post_id, username=username).delete()
        post.no_of_likes -= 1
        post.save()

    else:
        LikePost.objects.create(post_id=post_id, username=username)
        post.no_of_likes += 1
        post.save()
    return redirect('/')


@login_required
def settings(request):
    user_profile = Profile.objects.get(user=request.user)


    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
        else:
            image = request.FILES.get('image')

        bio = request.POST.get('bio')
        location = request.POST.get('location')

        user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        return redirect('/')

    context = {'user_profile': user_profile}
    return render(request, 'settings.html', context)

 
@login_required
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_posts_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).exists():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'
    
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_posts_length': user_posts_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following
    }

    return render(request, 'profile.html', context)


@login_required
def follow(request):
    if request.method == 'POST':
        follower = request.POST.get('follower')
        user = request.POST.get('user')

        if FollowersCount.objects.filter(follower=follower, user=user).exists():
            FollowersCount.objects.get(follower=follower, user=user).delete()
        else:
            FollowersCount.objects.create(follower=follower, user=user)
        return redirect('/profile/' + user)
    else:
        return redirect('/')



def signup(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username is already taken')
                return redirect(to='/signup/')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email is already taken')
                return redirect(to='/signup/')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                # user.save()


                # log in user and redirect it to settings page
                user_login = authenticate(request=request, username=username, password=password)
                if user_login:
                    login(request=request, user=user_login)


                # create a profile object for a new user
                new_profile = Profile(user=user, id_user=user.id)
                new_profile.save()

                messages.info(request, 'User created successfully')
                return redirect(to='/settings/')



        else:
            messages.info(request, 'Password does not match with Confirm Password')
            return redirect('/signup/')
    else:
        return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request=request, username=username, password=password)
        if user:
            login(request=request, user=user)
            messages.info(request, 'Login Successfuly')
            return redirect(to='/')
        else:
            messages.info(request, 'Invalid Credentials')


    return render(request, 'signin.html')

@login_required
def signout(request):
    logout(request)
    return redirect(to='/signin/')