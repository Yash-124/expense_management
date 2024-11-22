from django.urls import path
from . import views
from .views import signup

urlpatterns = [
    path('', signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('superuser-dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('submit-expense/', views.submit_expense, name='submit_expense'),
    path('user-submit-expense/', views.user_submit_expense, name='user_submit_expense'),
    path('delete-expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('delete-expense-in-dashboard/<int:expense_id>/', views.delete_expense_in_dashboard, name='delete_expense_in_dashboard'),
    path('user/update/<int:user_id>/', views.update_user, name='update_user'),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('users/manage/', views.manage_users, name='manage_users'),
    path('expense/approve/<int:expense_id>/', views.approve_expense, name='approve_expense'),
    path('expense/reject/<int:expense_id>/', views.reject_expense, name='reject_expense'),  
    path('superuser_settings/', views.superuser_settings, name='superuser_settings'),
    path('user_settings/', views.user_settings, name='user_settings'),

]
