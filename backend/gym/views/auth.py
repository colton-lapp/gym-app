from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout, get_user_model
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, response, status
from django.middleware.csrf import get_token

User = get_user_model()


def _normalize_email(raw):
    if not raw:
        return ""
    return raw.strip().lower()


# POST /api/auth/signup/
# payload: {email, password, access_code, first_name?, last_name?}
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signup(request):
    access_code = request.data.get("access_code")
    email_raw = request.data.get("email")
    password = request.data.get("password")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")

    # Validate access code
    if access_code != settings.SIGNUP_ACCESS_CODE:
        return response.Response(
            {"detail": "Invalid access code."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = _normalize_email(email_raw)

    if not email or not password:
        return response.Response(
            {"detail": "Email and password required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Case-insensitive uniqueness check
    if (
        User.objects.filter(email__iexact=email).exists()
        or User.objects.filter(username__iexact=email).exists()
    ):
        return response.Response(
            {"detail": "User already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Always store username/email lowercased
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=first_name or "",
        last_name=last_name or "",
    )

    # Auto-login after signup
    dj_login(request, user)

    # Optionally also set CSRF cookie here (same as login)
    resp = response.Response(
        {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
        status=status.HTTP_201_CREATED,
    )
    resp.set_cookie(
        "csrftoken",
        get_token(request),
        secure=True,
        httponly=False,
        samesite="None",
        domain=settings.CSRF_COOKIE_DOMAIN,
    )
    return resp


# POST /api/auth/login/
# payload: {email, password}
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    email = _normalize_email(request.data.get("email"))
    password = request.data.get("password")

    if not email or not password:
        return response.Response(
            {"detail": "Email and password required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Use normalized email for username
    user = authenticate(request, username=email, password=password)
    if not user:
        return response.Response(
            {"detail": "Invalid credentials."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    dj_login(request, user)

    resp = response.Response(
        {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
    )
    resp.set_cookie(
        "csrftoken",
        get_token(request),
        secure=True,
        httponly=False,
        samesite="None",
        domain=settings.CSRF_COOKIE_DOMAIN,
    )
    return resp


# POST /api/auth/logout/
@api_view(["POST"])
def logout(request):
    dj_logout(request)
    return response.Response({"detail": "Logged out."})


# GET/PATCH /api/auth/me/
@api_view(["GET", "PATCH"])
def me(request):
    if not request.user.is_authenticated:
        return response.Response(
            {"detail": "Not authenticated."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user = request.user

    if request.method == "GET":
        return response.Response(
            {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        )

    # PATCH
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

    return response.Response(
        {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
    )