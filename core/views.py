from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile, Post, LikePost, FallowersCount
from django.contrib.auth.decorators import login_required
from itertools import chain
import random
# Create your views here.


@login_required(login_url='signin')

@login_required(login_url='signin')
def index(request):
    user_obj = request.user
    profile_obj = Profile.objects.get(user=user_obj)

    user_fallowing_list = []
    feed = []

    user_fallowing = FallowersCount.objects.filter(fallower=request.user.username)

    for users in user_fallowing:
        user_fallowing_list.append(users.user)

    for usernames in user_fallowing_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    chained = chain(*feed)
    feed_lists = list(chained)

    # user suggestion starts
    all_users = User.objects.all()
    user_fallowing_all = []
    for user in user_fallowing:
        user_list = User.objects.get(username=user.user)
        user_fallowing_all.append(user_list)

    new_suggestions_list  = [x for x in list(all_users) if (x not in list(user_fallowing_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)
    print("final_suggestions_list", final_suggestions_list)

    username_profile = []
    username_profile_list = []
    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    return render(request, 'index.html', context={"profile_obj": profile_obj, "posts": feed_lists, "suggestions_username_profile_list": suggestions_username_profile_list[:4]})

@login_required(login_url='signin')
def upload(request):
    
    if request.method == "POST":
        username = request.user.username
        image = request.FILES.get("image_upload")
        caption = request.POST.get("caption")
        new_post = Post.objects.create(user=username, image=image, caption=caption)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')


@login_required(login_url='signin')
def search(request):
    user_obj = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_obj)

    if request.method == "POST":
        username = request.POST.get("username")
        username_obj = User.objects.filter(username__icontains=username)
        username_profile = []
        username_profile_list = []
        for users in username_obj:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

    username_profile_list = list(chain(*username_profile_list))
    return render(request, "search.html", {"user_profile": user_profile, "username_profile_list": username_profile_list})

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get("post_id")
    post = Post.objects.get(id=post_id)

    
    is_liked = LikePost.objects.filter(post_id=post_id, username=username).first()
    print("is_liked", is_liked)
    if not is_liked:
        LikePost.objects.create(post_id=post_id, username=username)
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        is_liked.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')

@login_required(login_url='signin')
def profile(request, pk):
    user_obj = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_obj)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    fallower = request.user.username
    user = pk
    if FallowersCount.objects.filter(fallower=fallower, user=user).first():
        button_text = "Unfallow"
    else:
        button_text = "Fallow"
    user_fallowers = len(FallowersCount.objects.filter(user=pk))
    user_fallowing = len(FallowersCount.objects.filter(fallower=pk))

    context = {
        "user_obj": user_obj,
        "user_profile": user_profile,
        "user_posts": user_posts,
        "user_post_length": user_post_length,
        "button_text": button_text,
        "user_fallowers": user_fallowers,
        "user_fallowing": user_fallowing,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def fallow(request):
    if request.method == "POST":
        fallower = request.POST.get("fallower")
        user = request.POST.get("user")
        fallower_user = FallowersCount.objects.filter(fallower=fallower, user=user).first()
        if fallower_user:
            fallower_user.delete()
            return redirect('/profile/'+user)
        else:
            FallowersCount.objects.create(fallower=fallower, user=user)
            return redirect('/profile/'+user)

    else:
        return redirect('/')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        image = request.FILES.get("image")
        if image:
            user_profile.profileimg = image
        bio = request.POST.get("bio", None)
        location = request.POST.get("location", None)
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        return redirect('settings')
    return render(request, "setting.html", context={"user_profile": user_profile})

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
                return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
    else:
        return render(request, 'signup.html')
    
def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print("username", username)
        print("password", password)
        user = auth.authenticate(username=username, password=password)
        print("user", user)
        if user:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
    else:
        return render(request, "signin.html")
    
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect("signin")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print("username", username)
        print("password", password)
        user = auth.authenticate(username=username, password=password)
        print("user", user)
        if user:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
    else:
        return render(request, "signin.html")
    
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect("signin")