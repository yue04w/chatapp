from django.urls import path
from users.views import login_page, logout_page, register_view
from . import views

urlpatterns = [
    path('', login_page, name="login"),
    path('logout/', logout_page, name="logout"),
    path('register/', register_view, name="register"),
]
