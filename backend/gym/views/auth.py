from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, response, status

# POST /api/auth/signup/
# payload: {email, password, access_code}
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signup(request):
    """
    TODO:
    - Validate access_code (hardcoded or from env)
    - Validate email/password
    - Create user with Django User model
    - Return token or success response
    """
    pass


# POST /api/auth/login/
# payload: {email, password}
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    """
    TODO:
    - Authenticate via email/password
    - Return JWT or session cookie
    """
    pass


# POST /api/auth/logout/
@api_view(["POST"])
def logout(request):
    """
    TODO:
    - Invalidate auth token or session
    """
    pass


# GET /api/auth/me/
@api_view(["GET"])
def me(request):
    """
    TODO:
    - Return the current user {id, email, name}
    """
    pass