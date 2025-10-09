from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUserManager(BaseUserManager):
    """Custom user manager that uses email as the unique identifier"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password"""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model that uses email for authentication
    Can identify whether a user is an admin or a student
    """
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # User type identification
    is_admin = models.BooleanField(default=False, help_text="Designates whether this user is an admin/teacher")
    is_student = models.BooleanField(default=True, help_text="Designates whether this user is a student")
    
    # Required fields for Django admin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Timestamps (Bonus requirement)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.email} ({'Admin' if self.is_admin else 'Student'})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Subject(models.Model):
    """
    Subject model - ensures unique subject names
    A specific subject should not exist twice (e.g., only one "Math" subject)
    """
    name = models.CharField(max_length=200, unique=True, help_text="Subject name must be unique")
    description = models.TextField(blank=True, null=True)
    
    # Timestamps (Bonus requirement)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Grade(models.Model):
    """
    Grade model - links students to subjects with their grades
    Allows students to take the same subject multiple times
    Grades can be initially blank
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='grades',
        limit_choices_to={'is_student': True}
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='grades'
    )
    
    # Grade can be blank initially (null=True, blank=True)
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Grade value between 0 and 100"
    )
    
    # Additional fields
    semester = models.CharField(max_length=50, blank=True, null=True, help_text="E.g., '1st Semester 2024'")
    school_year = models.CharField(max_length=20, blank=True, null=True, help_text="E.g., '2024-2025'")
    remarks = models.TextField(blank=True, null=True)
    
    # Timestamps (Bonus requirement)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Grade'
        verbose_name_plural = 'Grades'
        # Note: We don't use unique_together here because students can retake subjects
        ordering = ['-created_at']
    
    def __str__(self):
        grade_display = self.grade if self.grade is not None else "No Grade Yet"
        return f"{self.student.get_full_name()} - {self.subject.name}: {grade_display}"
    
    def is_passing(self, passing_grade=75):
        """Helper method to check if grade is passing"""
        if self.grade is None:
            return None
        return self.grade >= passing_grade