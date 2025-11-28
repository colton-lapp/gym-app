from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout, get_user_model
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, response, status
from django.middleware.csrf import get_token
from django.http import JsonResponse

User = get_user_model()

# POST /api/auth/signup/
# payload: {email, password, access_code}
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signup(request):
    access_code = request.data.get("access_code")
    email = request.data.get("email")
    password = request.data.get("password")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")

    # Validate access code
    if access_code != settings.SIGNUP_ACCESS_CODE:
        return response.Response(
            {"detail": "Invalid access code."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not email or not password:
        return response.Response(
            {"detail": "Email and password required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(email=email).exists():
        return response.Response(
            {"detail": "User already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create_user(username=email, email=email, password=password,
                                    first_name=first_name, last_name=last_name)

    # Auto-login after signup
    dj_login(request, user)

    return response.Response(
        {"id": user.id, "email": user.email,
         "first_name":user.first_name, "last_name":user.last_name},
        status=status.HTTP_201_CREATED,
    )


# POST /api/auth/login/
# payload: {email, password}
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(request, username=email, password=password)
    if not user:
        return response.Response(
            {"detail": "Invalid credentials."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    dj_login(request, user)
    response = JsonResponse({"status": "ok"})
    response["X-CSRFToken"] = get_token(request)
    return response.Response({"id": user.id, "email": user.email})


# POST /api/auth/logout/
@api_view(["POST"])
def logout(request):
    dj_logout(request)
    return response.Response({"detail": "Logged out."})


# GET /api/auth/me/
@api_view(["GET", "PATCH"])
def me(request):
    if not request.user.is_authenticated:
        return response.Response(
            {"detail": "Not authenticated."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if request.method == "GET":
        user = request.user
        return response.Response({"id": user.id, "email": user.email, "first_name": user.first_name, "last_name": user.last_name})

    elif request.method == "PATCH":
        user = request.user
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")

        changed = False
        if first_name is not None:
            user.first_name = first_name
            changed = True
        if last_name is not None:
            user.last_name = last_name
            changed = True

        if changed:
            user.save()

        return response.Response({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        })  
