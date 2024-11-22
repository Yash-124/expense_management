from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Add a currency field with choices
    class CurrencyChoices(models.TextChoices):
        USD = 'USD', 'US Dollar'
        EUR = 'EUR', 'Euro'
        GBP = 'GBP', 'British Pound'
        INR = 'INR', 'Indian Rupee'

    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.USD
    )

    def __str__(self):
        return self.user.username

    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    date_submitted = models.DateTimeField(auto_now_add=True)

    # * Added ApprovalStatus choices
    class ApprovalStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    # * Added approval_status field
    approval_status = models.CharField(
        max_length=10,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )

    class Category(models.TextChoices):
        TRAVELING = "TRAVELING", "Traveling"
        SERVICES = "SERVICES", "Services"
        FOOD = "FOOD", "Food"
        ENTERTAINMENT = "ENTERTAINMENT", "Entertainment"
        TRANSPORTATION = "TRANSPORTATION", "Transportation"
        HEALTH = "HEALTH", "Health"
        OTHER = "OTHER", "Other"

    category = models.CharField(
        max_length=255, choices=Category.choices, default=Category.OTHER
    )

    def __str__(self):
        return f"{self.user.username} - {self.amount}"
    
     # * Add a method to display the amount with currency
    def display_amount_with_currency(self):
        return f"{self.user.userprofile.currency} {self.amount}"



