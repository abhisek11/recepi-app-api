from django.urls import path
from user.knox_views import views as _views
from user import views


app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', _views.LogoutView.as_view(), name='logout'),
    path('logoutall/', _views.LogoutAllView.as_view(), name='logoutall'),

]
