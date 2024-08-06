from django.db import models
from datetime import date
from django.utils import timezone
from authentication.models import User
# Create your models here.

class Author(models.Model):
    full_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=timezone.now)
    updated_at = models.DateTimeField(auto_now=timezone.now)

    def __str__(self):
        return self.full_name
    
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    categories = models.CharField(max_length=255,blank=True,null=True)
    isbn = models.CharField(max_length=255, blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    cover_pic = models.URLField(max_length=500,blank=True,null=True)
    publisheddate = models.DateField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=timezone.now)
    updated_at = models.DateTimeField(auto_now=timezone.now)

    def __str__(self):
        return self.title
    
class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    note = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=timezone.now)
    updated_at = models.DateTimeField(auto_now=timezone.now)

class BookRating(models.Model):
    rating_choices = [('1', '1'),
                      ('1.5', '1.5'),
                      ('2', '2'),
                      ('2.5', '2.5'),
                      ('3', '3'),
                      ('3.5', '3,5'),
                      ('4', '4'),
                      ('4', '4.5'),
                      ('5', '5'), 
                      ("0", "0"),
                      ("0.5", "0.5")]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rate = models.CharField(max_length=255,blank=True,null=True,choices = rating_choices)
    created_at = models.DateTimeField(auto_now_add=timezone.now)
    updated_at = models.DateTimeField(auto_now=timezone.now)
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    comment = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=timezone.now)
    updated_at = models.DateTimeField(auto_now=timezone.now)

