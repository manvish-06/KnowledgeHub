from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect
from .forms import RegisterForm

def register(request):

    if request.method == "GET":
        form = RegisterForm()

        return render(request, "accounts/register.html",{
            "form": form
        }
    )

    form = RegisterForm(request.POST)

    if not form.is_valid():
        return render(request, "accounts/register.html",{
            "form": form
        }
    )

    username = form.cleaned_data["username"]
    email = form.cleaned_data["email"]
    password = form.cleaned_data["password"]
    confirmation = form.cleaned_data["confirmation"]

    if password != confirmation:

        return render(
            request,
            "accounts/register.html",
            {
                "form": form,
                "message": "Passwords must match."
            }
        )

    try:

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect("index")

    except IntegrityError:

        return render(
            request,
            "accounts/register.html",
            {
                "form": form,
                "message": "Username already exists."
            }
        )



def login_view(request):

    if request.method == "GET":
        return render(request, "accounts/login.html")

    username = request.POST["username"]
    password = request.POST["password"]

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is not None:

        login(request, user)

        return redirect("index")

    return render(
        request,
        "accounts/login.html",
        {
            "message": "Invalid username or password."
        }
    )

def logout_view(request):

    logout(request)

    return redirect("index")



