from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile, Post
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required(login_url='signin')

@login_required(login_url='signin')
def index(request):
    user_obj = request.user
    profile_obj = Profile.objects.get(user=user_obj)
    posts = Post.objects.all()
    
    return render(request, 'index.html', context={"profile_obj": profile_obj, "posts": posts})

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
    return HttpResponse("<h1>Upload View </h1>")

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