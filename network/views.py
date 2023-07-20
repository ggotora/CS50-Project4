from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import User, Profile
from django.http import JsonResponse
# imports 
from django.core.paginator import Paginator
from .models import Post 
from .forms import PostForm
import json


def index(request):
    form = PostForm()
    posts = Post.objects.order_by('-pub_date')
    preview_list = posts[:5]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return HttpResponseRedirect(reverse('index'))
    return render(request, "network/index.html", {'form': form, 'preview_list': preview_list, 'page_obj': page_obj})



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
    return HttpResponseRedirect(reverse('login'))

def following(request):
    if request.user.is_authenticated:
        following = request.user.profile.follows.all()
        profiles_followed = [_profile for _profile in following]
        return render(request, 'network/following.html', {'profiles_followed':profiles_followed })
    return HttpResponseRedirect(reverse('login'))

def edit(request, id):
    post = get_object_or_404(Post, id=id)
    form = PostForm(instance=post)
    is_owner = post.user == request.user
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
        return JsonResponse({"message": "updated"},safe=False)
    return render(request, "network/edit.html", {
        'form': form, 
        'is_owner': is_owner, 
        'id':id

    })

def like(request):
    data = json.loads(request.body)
    id = data["id"]
    post = get_object_or_404(Post, id=id)
    liked = ''
    if request.user.is_authenticated: 
        if post.likes.filter(id=request.user.id).exists():
            liked = "No"
            post.likes.remove(request.user)
        else:
            liked = "Yes"
            post.likes.add(request.user)
    new_data = {
             "liked": liked, 
            "count": post.likes.count()
        }
    return JsonResponse(new_data, safe=False)