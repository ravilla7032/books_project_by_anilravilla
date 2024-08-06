from django.urls import path
from . import views

urlpatterns = [

    # Author configurations
    path('author_search', views.AuthorConfigurations.as_view(http_method_names=['get']), name='Author search by name'),
    path('register_author', views.AuthorConfigurations.as_view(http_method_names=['post']), name='Register the Author'),
    path('update_authorinfo', views.AuthorConfigurations.as_view(http_method_names=['put']), name='update Author Information'),
    path('delete_author', views.AuthorConfigurations.as_view(http_method_names=['delete']), name='delete author'),

    # Books Confiruration
    path('searchtype_list', views.BookSearchKeywordList.as_view(http_method_names=['get']), name='List of searchtype'),
    path('book_search', views.BooksConfigurations.as_view(http_method_names=['get']), name='book search on google books'),
    path('register_book', views.BooksConfigurations.as_view(http_method_names=['post']), name='Book Registration'),
    path('update_book_info', views.BooksConfigurations.as_view(http_method_names=['put']), name='Update the Book Information'),
    path('delete_book', views.BooksConfigurations.as_view(http_method_names=['delete']), name='delete the Book'),

    # Recommendation Confiruration
    path('recommendedbooks_byuser', views.RecommendationConfigurations.as_view(http_method_names=['get']), name='all books recommended by a user'),
    path('recommend_a_book', views.RecommendationConfigurations.as_view(http_method_names=['post']), name='recommand a book'),
    path('delete_recommendation', views.RecommendationConfigurations.as_view(http_method_names=['delete']), name='delete the recommendation on a book'),

    # Rating Confiruration
    path('rating_list', views.RatingList.as_view(http_method_names=['get']), name='Rating list'),
    path('booksrated_byuser', views.BookRatingConfigurations.as_view(http_method_names=['get']), name='Books rated by a user'),
    path('rating_a_book', views.BookRatingConfigurations.as_view(http_method_names=['post']), name='Rate a Book'),
    path('delete_rating', views.BookRatingConfigurations.as_view(http_method_names=['delete']), name='Delete Rating on a Book'),

    # Cooments Confiruration
    path('commentedbooks_byuser', views.CommentsConfigurations.as_view(http_method_names=['get']), name='Books Commented by a user'),
    path('create_a_comment', views.CommentsConfigurations.as_view(http_method_names=['post']), name='Commenting on a book by user'),
    path('delete_comment', views.CommentsConfigurations.as_view(http_method_names=['delete']), name='delete the comment on book by user'),

    # Comman Apis
    path('most_recommended_books', views.MostRecommendedBooks.as_view(http_method_names=['get']), name='Most Recommended Books'),
    path('highest_rated_books', views.HighestRatingBooks.as_view(http_method_names=['get']), name='Highest Rating Books'),
    path('book_comments', views.AllCommentsOnBooks.as_view(http_method_names=['get']), name='Retrieving all comments on a book'),
    path('books_between_dates', views.BooksOnPublishedDates.as_view(http_method_names=['get']), name='search on all books between published dates'),


    
]
