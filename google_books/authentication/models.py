from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractUser, Group, Permission
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, age, mobile_number, password, is_staff=False, is_superuser=False, is_admin=False):
        if not (email, username, first_name, password):
            raise ValueError("User must have email, username, first_name, password.")
        
        user = self.model(email=self.normalize_email(email))
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.age = age
        user.mobile_number = mobile_number
        user.is_active = True
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.is_admin = is_admin
        
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, username, email, first_name, age, mobile_number, password, last_name=None):
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            age=age,
            mobile_number=mobile_number)
        
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractUser):
    mobile_number = models.BigIntegerField(unique=True)
    email = models.EmailField(verbose_name='email', max_length=500, unique=True)
    username = models.CharField(max_length=500, unique=True)
    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500, blank=True, null=True)
    age = models.IntegerField()
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=timezone.now)
    updated_at = models.DateTimeField(auto_now=timezone.now)

    # Add related_name attributes to avoid clashes
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Unique related_name
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',  # Unique related_name
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'mobile_number', 'age']

    objects = UserManager()

    def __str__(self):
        return self.username + ' , ' + self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True

class Profile(models.Model):
    gender_choices = [('Male', 'Male'),
                      ('Female', 'Female'),
                      ('Others', 'Others')]
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    bio = models.TextField(blank=True,null=True,max_length=2000)
    gender = models.CharField(max_length=100,blank=True,null=True,choices = gender_choices)
    last_login = models.DateTimeField(verbose_name='last login',auto_now=True)
    otp = models.IntegerField(blank=True,null=True)
    security_code = models.CharField(max_length=20,blank=True,null=True)
    security_code_validated_upto = models.DateTimeField(blank=True,null=True)
    verified = models.BooleanField(default=False)
    address = models.CharField(max_length=200,blank=True,null=True)
    forgot_password_token = models.CharField(max_length=5000,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=timezone.now)
    updated_at = models.DateTimeField(auto_now=timezone.now)

    def __str__(self):
        return self.user.first_name