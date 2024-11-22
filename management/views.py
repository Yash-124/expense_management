from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, ExpenseForm
from .models import Expense ,UserProfile
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .forms import UserCreationForm, CurrencyForm
from django.core.paginator import Paginator


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            # Show message to wait for confirmation
            messages.info(request, 'Signup successful! Please wait for confirmation from the backend to log in.')
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})
def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username') 
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                # Check if the user account is active
                if user.is_active:
                    # Ensure UserProfile exists before logging in
                    if not hasattr(user, 'userprofile'):
                        UserProfile.objects.create(user=user)

                    login(request, user)
                    # Check if the user is a superuser and redirect accordingly
                    if user.is_superuser:
                        return redirect('superuser_dashboard')
                    else:
                        return redirect('dashboard')
                else:
                    # Account is not active, show a message
                    messages.error(request, 'Wait for your account to be activated.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'user_login.html', {'form': form})


@login_required
def superuser_dashboard(request):
    # Redirect if the user is not a superuser
    if not request.user.is_superuser:
        return redirect('dashboard')

    # Get all users and expenses
    users = User.objects.all()
    expenses = Expense.objects.all().order_by('-date_submitted')  # Order by date_submitted descending

    # Handle user creation form submission
    if request.method == 'POST' and 'user_creation_form' in request.POST:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)  # Create a UserProfile for the new user
            messages.success(request, 'New user created successfully.')
            return redirect('superuser_dashboard')
    else:
        form = UserCreationForm()

    # Set up pagination for users
    user_paginator = Paginator(users, 5)  # Show 5 users per page
    user_page_number = request.GET.get('page_users')  # Use 'page_users' for user pagination
    paginated_users = user_paginator.get_page(user_page_number)

    # Set up pagination for expenses
    expense_paginator = Paginator(expenses, 5)  # Show 5 expenses per page
    expense_page_number = request.GET.get('page_expenses')  # Use 'page_expenses' for expense pagination
    paginated_expenses = expense_paginator.get_page(expense_page_number)

    # Prepare context for the template
    context = {
        'users': paginated_users,
        'expenses': paginated_expenses,
        'form': form
    }

    # Render the dashboard template with the context
    return render(request, 'superuser_dashboard.html', context)

@login_required
def dashboard(request):
    if not request.user.is_active:
        return redirect('login')

    # Get user's expenses
    expenses = Expense.objects.filter(user=request.user).order_by('-date_submitted')  # Order by date_submitted descending

    # Set up pagination for expenses
    expense_paginator = Paginator(expenses, 5)  # Show 5 expenses per page
    page_number = request.GET.get('page')
    paginated_expenses = expense_paginator.get_page(page_number)

    return render(request, 'dashboard.html', {'expenses': paginated_expenses})

@login_required
def submit_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('superuser_dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'superuser_submit_expense.html', {'form': form})

@login_required
def user_submit_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'user_submit_expense.html', {'form': form})

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    expense.delete()
    return redirect('superuser_dashboard')

@login_required
def delete_expense_in_dashboard(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    expense.delete()
    return redirect('dashboard')


@login_required
def update_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('superuser_dashboard')
    else:
        form = UserChangeForm(instance=user)
    
    return render(request, 'update_user.html', {'form': form})

@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('superuser_dashboard')

@login_required
def manage_users(request):
    if not request.user.is_superuser:
        return redirect('dashboard')  # Only allow superusers to access this page

    users = User.objects.all()

    # Set up pagination (show 10 users per page)
    paginator = Paginator(users, 5)
    page_number = request.GET.get('page')
    paginated_users = paginator.get_page(page_number)

    # Handle user creation
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New user created successfully.')
            return redirect('manage_users')
    else:
        form = UserCreationForm()

    context = {
        'users': paginated_users,  # Pass the paginated users
        'form': form
    }

    return render(request, 'manage_users.html', context)


@login_required
def approve_expense(request, expense_id):
    if not request.user.is_superuser:  # Only superusers can approve/reject
        return redirect('dashboard')
    
    expense = get_object_or_404(Expense, id=expense_id)
    
    expense.approval_status = Expense.ApprovalStatus.APPROVED
    expense.save()
    
    messages.success(request, f'Expense {expense.description} has been approved.')
    return redirect('superuser_dashboard')

@login_required
def reject_expense(request, expense_id):
    if not request.user.is_superuser:  # Only superusers can approve/reject
        return redirect('dashboard')
    
    expense = get_object_or_404(Expense, id=expense_id)
    
    # * Notify the user and delete the rejected expense
    messages.error(request, f'Expense {expense.description} has been rejected and removed.')
    expense.delete()  # Rejected expenses are not saved in the database
    
    return redirect('superuser_dashboard')

@login_required
def superuser_settings(request):
    if not request.user.is_superuser:
        return redirect('dashboard')

    # Handle currency settings form submission for superusers
    try:
        currency_form = CurrencyForm(request.POST or None, instance=request.user.userprofile)
        if request.method == 'POST' and currency_form.is_valid():
            currency_form.save()
            messages.success(request, 'Currency preference updated.')
            return redirect('superuser_settings')
    except UserProfile.DoesNotExist:
        # If UserProfile doesn't exist, create it
        request.user.userprofile = UserProfile.objects.create(user=request.user)
        currency_form = CurrencyForm(instance=request.user.userprofile)

    return render(request, 'superuser_settings.html', {'currency_form': currency_form})

@login_required
def user_settings(request):
    if not request.user.is_active:
        return redirect('login')

    # Handle currency settings form submission for regular users
    try:
        currency_form = CurrencyForm(request.POST or None, instance=request.user.userprofile)
        if request.method == 'POST' and currency_form.is_valid():
            currency_form.save()
            messages.success(request, 'Currency preference updated.')
            return redirect('user_settings')
    except UserProfile.DoesNotExist:
        # If UserProfile doesn't exist, create it
        request.user.userprofile = UserProfile.objects.create(user=request.user)
        currency_form = CurrencyForm(instance=request.user.userprofile)

    return render(request, 'user_settings.html', {'currency_form': currency_form})


def user_logout(request):
    logout(request)
    return redirect('login')

