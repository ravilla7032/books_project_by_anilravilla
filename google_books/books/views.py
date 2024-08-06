from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import json,os, ipdb, re
from django.db.models import F,Q,Count,Avg,FloatField
from django.db.models.functions import Cast
from googleapiclient.discovery import build
from django.db import transaction

from .models import Author, Book, Recommendation, BookRating, Comment
from authentication.helpers import url_validator
from authentication.models import User

class BooksConfigurations(APIView):
    def get(self, request):
        request = request.GET
        if not (len(request.keys()) == 2 and all(key in request for key in ["search_key", "search_type"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)

        search_key = request.get("search_key")
        search_type = request.get("search_type")
        if not (search_key and search_type and search_type in ("keyword", "title", "author", "categories")):
            return Response({"message": "Invalid or missing required request data.", "status": False}, status=status.HTTP_400_BAD_REQUEST)

        api_key = "AIzaSyBQAeOWiY-UAgckgEYPQskU2oNG0JhHniY"
        service = build("books", "v1", developerKey=api_key)
        # Fetch books from Google Books API
        response = service.volumes().list(q=search_key).execute()
        books = response.get("items", [])

        def date_setter(date_str):
            if not date_str: return None
            try: return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                try: return datetime.strptime(date_str, "%Y").date()
                except ValueError: return None
        try:
            formatted_books = []
            for book in books:
                volume_info = book.get("volumeInfo", {})
                formatted_books.append({
                    "title": volume_info.get("title", "").lower(),
                    "authors": [author.lower() for author in volume_info.get("authors", [])],
                    "categories": ", ".join(volume_info.get("categories", [])).lower(),
                    "isbn": next((rec["identifier"].lower() for rec in volume_info.get("industryIdentifiers", []) if rec["type"] == "ISBN_10"), None),
                    "cover_pic": volume_info.get("imageLinks", {}).get("thumbnail"),
                    "publisheddate": date_setter(volume_info.get("publishedDate")),
                    "description": volume_info.get("description", "").lower()
                })

            with transaction.atomic():
                for book_data in formatted_books:
                    for author_name in book_data["authors"]:
                        author, created = Author.objects.get_or_create(full_name=author_name)

                        Book.objects.update_or_create(
                            title=book_data["title"],
                            author=author,
                            defaults={
                                "categories": book_data["categories"],
                                "isbn": book_data["isbn"],
                                "description": book_data["description"],
                                "cover_pic": book_data["cover_pic"],
                                "publisheddate": book_data["publisheddate"] or None,
                            }
                        )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            search_key_lower = search_key.lower()
            books_query = Book.objects.all()

            if search_type == "keyword":
                books_query = books_query.filter(Q(title__icontains=search_key_lower) | Q(author__full_name__icontains=search_key_lower) |
                    Q(categories__icontains=search_key_lower) | Q(description__icontains=search_key_lower))
            elif search_type == "title":
                books_query = books_query.filter(title__icontains=search_key_lower)
            elif search_type == "author":
                books_query = books_query.filter(author__full_name__icontains=search_key_lower)
            elif search_type == "categories":
                books_query = books_query.filter(categories__icontains=search_key_lower)

            search_results = [
                {"book_id":book.pk, "title": book.title, "author": book.author.full_name, "author_id": book.author.pk, "categories": book.categories, 
                "isbn": book.isbn, "cover_pic": book.cover_pic, "publisheddate": book.publisheddate, "description": book.description,
                "recommended_by":Recommendation.objects.filter(book__id=book.pk).count(),"comments":Comment.objects.filter(book__id=book.pk).values("comment"),
                "rating":BookRating.objects.filter(book__id=book.pk).annotate(numeric_rate=Cast('rate', FloatField())).aggregate(avg_rating=Avg('numeric_rate'))['avg_rating']}
                for book in books_query
            ]
            return Response(search_results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self,request):
        data = request.data
        if not (type(data)==dict and len(data.keys())==7 and all(key in data for key in ["title", "author_id", "cover_pic", "categories", "isbn", "description", "publisheddate"])):
            return Response({"message": "The request data is invalid.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        
        title = data.get("title")
        author_id = data.get("author_id")
        cover_image = data.get("cover_pic")
        categories = data.get("categories")
        isbn = data.get("isbn")
        description = data.get("description")
        publisheddate = data.get("publisheddate")
        types = (str, type(None))
        if not(title and type(title)==str and author_id and type(author_id)==int and categories and type(categories)==str and (type(publisheddate) in types) and (type(isbn) in types) and (type(cover_image) in types) and (type(description) in types)):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        if cover_image and not url_validator(url=cover_image):
            return Response({'message':'Invalid cover_pic.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        try : publisheddate = datetime.strptime(publisheddate, "%Y-%m-%d").date()
        except: return Response({"message":"Invalid published date; the published date must be in 'YYYY-MM-DD' format.", "status":False}, status=status.HTTP_400_BAD_REQUEST)

        if Book.objects.filter(title=title.lower(), author__id=author_id).first():
            return Response({"message": "A book is already registered under the author's title", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        
        author_obj = Author.objects.filter(id=author_id).first()
        if not author_obj:
            return Response({"message": "No Author was found with the request data.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        
        book_obj = Book.objects.create(title=title.lower(), author=author_obj, categories=categories.lower(), isbn=isbn, description=description.lower(), cover_pic=cover_image, publisheddate=publisheddate)
        return Response({"message":"The book was successfully registered.","book_id":book_obj.pk, "title":book_obj.title, "status":True}, status=status.HTTP_201_CREATED)
    
    def put(self,request):
        data = request.data
        if not (type(data)==dict and len(data.keys())==8 and all(key in data for key in ["book_id", "title", "author_id", "cover_pic", "categories", "isbn", "description", "publisheddate"])):
            return Response({"message": "The request data is invalid.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        
        book_id = data.get("book_id")
        title = data.get("title")
        author_id = data.get("author_id")
        cover_image = data.get("cover_pic")
        categories = data.get("categories")
        isbn = data.get("isbn")
        description = data.get("description")
        publisheddate = data.get("publisheddate")
        types = (str, type(None))
        if not(book_id and type(book_id)==int and title and type(title)==str and author_id and type(author_id)==int and (type(cover_image) in types) and (type(publisheddate) in types) and categories and type(categories)==str and (type(isbn) in types) and (type(description) in types)):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        if cover_image and not url_validator(url=cover_image):
            return Response({'message':'Invalid cover_pic.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        try : publisheddate = datetime.strptime(publisheddate, "%Y-%m-%d").date()
        except: return Response({"message":"Invalid published date; the published date must be in 'YYYY-MM-DD' format.", "status":False}, status=status.HTTP_400_BAD_REQUEST)

        author_obj = Author.objects.filter(id=author_id).first()
        book_obj = Book.objects.filter(id=book_id, author__id=author_id).first()
        if not author_obj:
            return Response({"message": "No Author was found with the request data.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        if not book_obj:
            return Response({"message": "No Book was found with the request data.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        if Book.objects.filter(title=title.lower(), author__id=author_id).exclude(id=book_id, author__id=author_id):
            return Response({"message": "A book is already registered under the author's title.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        
        book_obj.title = title.lower()
        book_obj.author = author_obj
        book_obj.categories = categories.lower()
        book_obj.isbn = isbn
        book_obj.description = description
        book_obj.cover_pic = cover_image
        book_obj.publisheddate=publisheddate
        book_obj.save()
        return Response({"message":"The book Information was successfully Updated.","book_id":book_obj.pk, "title":book_obj.title, "status":True}, status=status.HTTP_201_CREATED)
    
    def delete(self, request):
        request = request.GET
        if not(len(request.keys())==1 and all(key in request for key in ["book_id"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        book_id = request.get("book_id")
        if not(book_id and book_id.isdigit()):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        book_obj = Book.objects.filter(id=book_id).first()
        if not book_obj:
            return Response({"message": "No Book was found with the request data.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        book_obj.delete()
        return Response({'message':'Book was successfully delete.', "status":True}, status=status.HTTP_200_OK)

class BookSearchKeywordList(APIView):
    def get(self, request):
        return Response(["keyword", "title", "author", "categories"], status=status.HTTP_200_OK)

class AuthorConfigurations(APIView):
    def get(self, request):
        request = request.GET
        if not(len(request.keys())==1 and all(key in request for key in ["author_name"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)

        author_name = request.get('author_name')
        if not author_name:
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        
        author_objs = Author.objects.all()
        matched_data = author_objs.filter(full_name__contains=author_name.lower()).annotate(author_id=F("id")).values("full_name", "author_id")
        if matched_data: return Response({'data':matched_data,'status':True}, status=status.HTTP_200_OK)
        else: return Response({'data':matched_data,'status':False}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        if not (type(data)==dict and len(data.keys())==1 and all(key in data for key in ["full_name"])):
            return Response({"message": "The request data is invalid",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        full_name = data.get("full_name")
        if not(full_name and type(full_name)==str):
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        if Author.objects.filter(full_name=full_name.lower()):
            return Response({"message": "There was an author on the specified name.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        Author.objects.create(full_name=full_name.lower())
        return Response({"message":"Author successfully registered.", "status":True}, status=status.HTTP_201_CREATED)
    
    def put(self, request):
        data = request.data
        if not (type(data)==dict and len(data.keys())==2 and all(key in data for key in ["author_id", "full_name"])):
            return Response({"message": "The request data is invalid",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        author_id = data.get("author_id")
        full_name = data.get("full_name")
        if not(author_id and type(author_id)==int and full_name and type(full_name)==str):
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        author_obj = Author.objects.filter(id=author_id).first()
        if not author_obj:
            return Response({"message": "No Author was found with the request data.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        if Author.objects.filter(full_name=full_name.lower()).exclude(id=author_id):
            return Response({"message": "There was an author on the specified name.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        
        author_obj.full_name = full_name.lower()
        author_obj.save()
        return Response({"message":"Author Information has been successfully updated.", "status":True}, status=status.HTTP_200_OK)
    
    def delete(self, request):
        request = request.GET
        if not(len(request.keys())==1 and all(key in request for key in ["author_id"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)

        author_id = request.get("author_id")
        if not(author_id and author_id.isdigit()):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        
        author_obj = Author.objects.filter(id=author_id).first()
        if not author_obj:
            return Response({"message": "No Author was found with the request data.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        author_obj.delete()
        return Response({'message':'Author was successfully delete.', "status":True}, status=status.HTTP_200_OK)


class RecommendationConfigurations(APIView):
    def get(self, request):
        request = request.GET
        if not(len(request.keys())==1 and all(key in request for key in ["user_id"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        user_id = request.get('user_id')
        if not (user_id and user_id.isdigit()):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(id=user_id):
            return Response({"message": "No user was found matching the provided request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        resp = Recommendation.objects.filter(user__id=user_id).annotate(recommendation_id=F("id"), title=F("book__title"), author_name=F("book__author__full_name"), author_id=F("book__author__id"), categories=F("book__categories"), publisheddate=F("book__publisheddate"), isbn=F("book__isbn"), cover_pic=F("book__cover_pic"), description=F("book__description"))\
            .values("recommendation_id", "title", "author_name", "author_id", "categories", "publisheddate", "isbn", "cover_pic", "description")
        return Response(resp, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        if not (type(data)==dict and len(data.keys())==3 and all(key in data for key in ["user_id", "book_id", "note"])):
            return Response({"message": "The request data is invalid",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        user_id = data.get("user_id")
        book_id = data.get("book_id")
        note = data.get("note")
        if not(user_id and type(user_id)==int and book_id and type(book_id)==int and (type(note) in (str, type(None)))):
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        
        user_obj = User.objects.filter(id=user_id).first()
        book_obj = Book.objects.filter(id=book_id).first()
        if not (user_obj and book_obj):
            return Response({"message": "Using the request data, no user or book was found.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        if Recommendation.objects.filter(user=user_obj, book=book_obj):
            return Response({"message": f"The book titled '{book_obj.title}' was already recommended by {user_obj.first_name}.", "status": False}, status=status.HTTP_400_BAD_REQUEST)

        recom_obj = Recommendation.objects.create(user=user_obj, book=book_obj, note=note)
        return Response({"message":f"The book titled '{recom_obj.book.title}' recommended by {recom_obj.user.first_name}.", "status":True}, status=status.HTTP_201_CREATED)
    
    def delete(self, request):
        request = request.GET
        if not(len(request.keys())==1 and all(key in request for key in ["recommendation_id"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        recommendation_id = request.get("recommendation_id")
        if not(recommendation_id and recommendation_id.isdigit()):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        recomm_obj = Recommendation.objects.filter(id=recommendation_id).first()
        if not recomm_obj:
            return Response({"message": "No Recommandation was found with the request data.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        recomm_obj.delete()
        return Response({'message':'Recommandation was successfully delete.', "status":True}, status=status.HTTP_200_OK)

class RatingList(APIView):
    def get(self, request):
        return Response(["0", "0.5", "1", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5"], status=status.HTTP_200_OK)

class BookRatingConfigurations(APIView):
    def get(self, request):
        request = request.GET
        if not(len(request.keys())==1 and all(key in request for key in ["user_id"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        user_id = request.get('user_id')
        if not (user_id and user_id.isdigit()):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        
        if not User.objects.filter(id=user_id):
            return Response({"message": "No user was found matching the provided request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        resp = BookRating.objects.filter(user__id=user_id)\
            .annotate(rating_id=F("id"), rating=F("rate"), title=F("book__title"), author_name=F("book__author__full_name"), author_id=F("book__author__id"), categories=F("book__categories"), isbn=F("book__isbn"), cover_pic=F("book__cover_pic"), publisheddate=F("book__publisheddate"), description=F("book__description"))\
            .values("title", "author_name", "author_id", "categories", "isbn", "cover_pic", "description", "rating", "rating_id", "publisheddate")
        return Response(resp, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data
        if not (type(data)==dict and len(data.keys())==3 and all(key in data for key in ["user_id", "book_id", "rating"])):
            return Response({"message": "The request data is invalid",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        user_id = data.get("user_id")
        book_id = data.get("book_id")
        rating = data.get("rating")
        if not(user_id and type(user_id)==int and book_id and type(book_id)==int and rating and (rating in ["0", "0.5", "1", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5"])):
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        
        user_obj = User.objects.filter(id=user_id).first()
        book_obj = Book.objects.filter(id=book_id).first()
        if not (user_obj and book_obj):
            return Response({"message": "Using the request data, no user or book was found.", "status": False}, status=status.HTTP_400_BAD_REQUEST)

        rating, created = BookRating.objects.update_or_create(user=user_obj,book=book_obj,defaults={'rate': rating})
        if created: return Response({"message":"A new rating was created.", "status":True}, status=status.HTTP_201_CREATED)
        else:return Response({"message":"The existing rating was updated.", "status":True}, status=status.HTTP_200_OK)
    
    def delete(self, request):
        request = request.GET
        if not(len(request.keys())==1 and all(key in request for key in ["rating_id"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        rating_id = request.get("rating_id")
        if not(rating_id and rating_id.isdigit()):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        
        rate_obj = BookRating.objects.filter(id=rating_id).first()
        if not rate_obj:
            return Response({"message": "No rating was found with the request data.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        rate_obj.delete()
        return Response({'message':'Rating on Book was successfully delete.', "status":True}, status=status.HTTP_200_OK)
    
class CommentsConfigurations(APIView):
    def get(self, request):
        request = request.GET
        if not(len(request.keys())==1 and all(key in request for key in ["user_id"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        user_id = request.get('user_id')
        if not (user_id and user_id.isdigit()):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(id=user_id):
            return Response({"message": "No user was found matching the provided request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        
        resp = Comment.objects.filter(user__id=user_id).annotate(comment_id=F("id"), title=F("book__title"), author_name=F("book__author__full_name"), author_id=F("book__author__id"), categories=F("book__categories"), isbn=F("book__isbn"), publisheddate=F("book__publisheddate"), cover_pic=F("book__cover_pic"), description=F("book__description"))\
            .values("comment", "comment_id", "title", "author_name", "author_id", "categories", "isbn", "cover_pic", "description", "publisheddate")
        return Response(resp, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data
        if not (type(data)==dict and len(data.keys())==3 and all(key in data for key in ["user_id", "book_id", "comment"])):
            return Response({"message": "The request data is invalid",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        user_id = data.get("user_id")
        book_id = data.get("book_id")
        comment = data.get("comment")
        if not(user_id and type(user_id)==int and book_id and type(book_id)==int and comment and type(comment)==str):
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        
        user_obj = User.objects.filter(id=user_id).first()
        book_obj = Book.objects.filter(id=book_id).first()
        if not (user_obj and book_obj):
            return Response({"message": "Using the request data, no user or book was found.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        comment, created = Comment.objects.update_or_create(user=user_obj,book=book_obj,comment=comment)
        if created: return Response({"message":"A new Comment was created.", "status":True}, status=status.HTTP_201_CREATED)
        else:return Response({"message":"The existing Comment was updated.", "status":True}, status=status.HTTP_200_OK)
    
    def delete(self, request):
        request = request.GET
        if not(len(request.keys())==1 and all(key in request for key in ["comment_id"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        comment_id = request.get("comment_id")
        if not(comment_id and comment_id.isdigit()):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        comment_obj = Comment.objects.filter(id=comment_id).first()
        if not comment_obj:
            return Response({"message": "No Comment was found with the request data.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        comment_obj.delete()
        return Response({'message':'Comment was successfully delete.', "status":True}, status=status.HTTP_200_OK)
    

class MostRecommendedBooks(APIView):
    def get(self, request):
        resp = Book.objects.annotate(num_recommendations=Count('recommendation')).order_by('-num_recommendations')\
            .annotate(book_id=F('id'),author_name=F('author__full_name'))\
            .values('book_id', "author_id", 'title', 'author_name', 'categories','isbn', 'cover_pic', 'publisheddate', 'description','num_recommendations')
        return Response(resp, status=status.HTTP_200_OK)

class HighestRatingBooks(APIView):
    def get(self, request):
        resp = Book.objects.annotate(avg_rating=Avg(Cast('bookrating__rate', FloatField()))).filter(~Q(avg_rating=None)).order_by('-avg_rating')\
            .annotate(book_id=F('id'),author_name=F('author__full_name'))\
            .values('book_id',"author_id", 'title', 'author_name', 'categories','isbn', 'cover_pic', 'publisheddate', 'description','avg_rating')
        return Response(resp, status=status.HTTP_200_OK)
    
class AllCommentsOnBooks(APIView):
    def get(self, request):
        request = request.GET
        if not(len(request.keys())==1 and all(key in request for key in ["book_id"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        book_id = request.get('book_id')
        if not (book_id and book_id.isdigit()):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)

        book_obj = Book.objects.filter(id=book_id).first()
        if not book_obj:
            return Response({"message": "No Book was found with the request data.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        resp = Comment.objects.filter(book__id=book_id).annotate(user_name=F("user__first_name")).values("user_name", "comment")
        return Response(resp, status=status.HTTP_200_OK)

class BooksOnPublishedDates(APIView):
    def get(self, request):
        request = request.GET
        if not(len(request.keys())==2 and all(key in request for key in ["start_date", "end_date"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        start_date = request.get('start_date')
        end_date = request.get('end_date')
        if not (start_date and end_date):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        try:
            start_date = datetime.strptime(f"{start_date}", "%Y-%m-%d")
            end_date = datetime.strptime(f"{end_date}", "%Y-%m-%d")
        except: return Response({"message": "Invalid dates; The date must be in the format yyyy-mm-dd.", "status":False}, status=status.HTTP_400_BAD_REQUEST)
        if start_date > end_date:
            return Response({"message": "The start time must not exceed the end time.", "status":False}, status=status.HTTP_400_BAD_REQUEST)

        resp = Book.objects.filter(publisheddate__range=[start_date, end_date]).annotate(book_id=F("id"), author_name=F("author__full_name"))\
            .values("book_id", "author_id", "title", "author_name", "categories", "isbn", "cover_pic", "publisheddate", "description")
        return Response(resp, status=status.HTTP_200_OK)

