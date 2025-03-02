from django.contrib.auth import views as auth_views
from django.urls import path
from vector_search.views import summarize, get_user_summaries, dashboard,register,search,get_search_summary

urlpatterns = [
    path("summarize/", summarize, name="summarize"),
    path("summaries/", get_user_summaries, name="get_user_summaries"),
    path("dashboard/", dashboard, name="dashboard"),
    path('search/',search,name="search"),
    path('get_search_term/',get_search_summary,name='get_search_term'),

    # ✅ Authentication
    path("login/", auth_views.LoginView.as_view(template_name="vector_search/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", register, name="register"),
]
