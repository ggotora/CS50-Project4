from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import User, Profile

# imports 
from django.views import generic
from .models import Post 
from .forms import PostForm


def index(request):
    form = PostForm()
    posts = Post.objects.order_by('-pub_date')
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return HttpResponseRedirect(reverse('index'))
    return render(request, "network/index.html", {'form': form, 'posts': posts})



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    
def profile(request, id):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(id=id)
            
        except (KeyError, Profile.DoesNotExist):
            return render(request, "network/profile.html", {"error_message":"Error"})
        else:
            user_posts = profile.user.post_set.all()
            following = profile.follows.all()
        if request.method == 'POST':
            follow = request.POST.get('follow')
            if follow == "follow":
                request.user.profile.follows.add(profile)
                request.user.profile.save()
                return HttpResponseRedirect(reverse('profile', args=(id,)))
            else:
                request.user.profile.follows.remove(profile)
                request.user.profile.save()
                return HttpResponseRedirect(reverse('profile', args=(id,)))
        return render(request, "network/profile.html", {'profile': profile, 'user_posts': user_posts})

def following(request):
    if request.user.is_authenticated:
        following = request.user.profile.follows.all()
        profiles_followed = [_profile for _profile in following]
        return render(request, 'network/following.html', {'profiles_followed':profiles_followed })
    return HttpResponseRedirect(reverse('login'))