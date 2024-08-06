# books_project_by_anilravilla

# Setup Instructions

1. Clone the Repository:
  git clone https://github.com/ravilla7032/books_project_by_anilravilla.git
  cd google_books

2. Create and Activate Virtual Environment:
  python -m venv venv
  source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install Dependencies:
  pip install -r requirements.txt

4. Create the PostgreSQL Database:
  Create a PostgreSQL database named books_buzz and a user named admin1 with the password admin@123. Grant all privileges on the database to this user.
  Save the database details for later use in a .env file with the following entries: DB_NAME=books_buzz, DB_USER=admin1, and DB_PASSWORD=admin@123.
  
5. Configure Environment Variables:
   Create a .env file in the project root and add the following:
   ```plaintext
    DEBUG=1
    SECRET_KEY='django-insecure-fgi*9*)xsd=p=^d)$a*5b%ms^9efm4e*(7ybwk65xl3!u4+g1)'
   
    DB_ENGINE='django.db.backends.postgresql'
    DB_NAME='books_buzz'
    DB_USER='admin1'
    DB_PASSWORD='admin@123'
    DB_HOST='localhost'
    DB_PORT='5432'
    
    DEFAULT_FROM_EMAIL='ravilla.anil3@gmail.com'  # your mail
    EMAIL_HOST_USER='ravilla.anil3@gmail.com'  # your mail
    EMAIL_HOST_PASSWORD='kgcg wjng cpiv yfxb'  # your App password
    EMAIL_PORT=587
    EMAIL_USE_TLS=True

7. Apply Migrations:

  • python manage.py makemigrations
  • python manage.py migrate


# Api Endpoints

Access all API endpoints through the Postman collection link below. This collection provides comprehensive API documentation, including details on requests, responses, exceptions, and additional notes for each endpoint.
This collection provides comprehensive API documentation, including details on requests, responses, exceptions, and additional notes for each endpoint.

Postman Collection Link: https://documenter.getpostman.com/view/37485860/2sA3rxrtna


# Google Books API Integration

The BooksConfigurations API endpoint is designed to search for books using the Google Books API. It allows users to search for books based on different criteria such as keyword, title, author, and categories. The results from the Google Books API are fetched, processed, and stored in the local database for further querying and retrieval.

Key Features:

1. Book Search
   
  --> The API accepts a search key and a search type as query parameters. The search type can be one of the following: "keyword", "title", "author", or "categories".
  --> The search key is used to query the Google Books API to retrieve a list of books that match the criteria.
  
2. Book Retrieval

  --> The API fetches book data from the Google Books API using the service.volumes().list(q=search_key).execute() method.
  --> The retrieved data includes information such as title, authors, categories, ISBN, cover picture, published date, and description.

3. Data Processing and Storage

  --> The API processes the retrieved book data to ensure it is in the correct format.
  --> Books and authors are saved to the local database. If an author or book already exists, it updates the existing record with the new information.

4. Display of Search Results

  --> After processing and storing the data, the API searches the local database based on the provided search type and key.
  --> It filters the results and returns a list of books that match the search criteria, including additional details such as the number of recommendations, comments, and average   rating.

5. Error Handling

  --> The API includes error handling to manage potential exceptions during data retrieval, processing, and storage, returning appropriate error messages if something goes wrong.


Example Workflow


1. Search Request:

  --> A client sends a GET request to the /api/book_search endpoint with parameters like search_key and search_type.
Example: http://127.0.0.1:8000/api/books/book_search?search_type=title&search_key=pirates

2. Google Books API Interaction:

  --> The API uses the Google Books API key to fetch data related to the search key.
  --> The Google Books API is queried, and results are returned as a JSON object.
  
3. Processing Results:

  --> The retrieved books are processed, extracting relevant information and formatting it for storage.
  --> Books and authors are saved to the local database with get_or_create and update_or_create methods.

4. Returning Results:

  --> The processed books are then filtered based on the search type and search key.
  --> A list of books is returned, including details like the number of recommendations, comments, and average ratings.

5. Response:

-->  A successful response includes a JSON list of books matching the search criteria, with detailed information for each book.
-->  In case of errors, an error message and status code are returned.


# Authentication Features

The authentication module of this project includes the following functionalities:

  --> User Registration: Allows users to sign up by providing their email, username, first name, last name, mobile number, age, and password. Email and mobile numbers must be unique.

  --> Password Reset: Users can request a password reset by submitting their email. An OTP (One-Time Password) is sent to the provided email for verification.

  --> OTP Verification: Users verify their OTP received during the password reset process. If the OTP is valid and not expired, the user can proceed with resetting their password.

  --> Password Reset: After verifying the OTP, users can reset their password if it meets the required complexity. The system ensures that new passwords are different from previous ones.


All API endpoints for the authentication module are documented in a Postman collection. This collection includes details on:

  --> Endpoints, Requests, Responses, Exceptions and API Documentation

  --> Postman Collection Link: https://documenter.getpostman.com/view/37485860/2sA3rxrtna


# Backend API Implementation

1. Models:

The google_books project includes the following core models:
  --> Author: Represents book authors.
  --> Book: Represents books, including details such as title, author, categories, and cover image.
  --> Recommendation: Represents user recommendations for books.
  --> BookRating: Represents ratings given by users to books.
  --> Comment: Represents user comments on books.

Example Model Implementation:

class Author(models.Model):
    full_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    categories = models.CharField(max_length=255, blank=True, null=True)
    isbn = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    cover_pic = models.URLField(max_length=500, blank=True, null=True)
    publisheddate = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BookRating(models.Model):
    rating_choices = [('1', '1'), ('1.5', '1.5'), ('2', '2'), ('2.5', '2.5'), ('3', '3'), ('3.5', '3.5'), ('4', '4'), ('4.5', '4.5'), ('5', '5'), ('0', '0'), ('0.5', '0.5')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rate = models.CharField(max_length=255, blank=True, null=True, choices=rating_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


2. Serializer Usage

In the google_books project, the UserSerializer is employed to manage user registration functionality. It is utilized to validate and serialize user data submitted during the signup process.
  --> File: serializers.py
  --> Purpose: The UserSerializer handles the user data input, ensuring that required fields are correctly filled and validated. It defines the structure and validation rules for user attributes such as first_name, last_name, email, and password.

* Application
--> View Integration: The UserSerializer is used in the RegisterUser API view to process registration requests. It validates incoming data, performs checks on mobile numbers and emails, and manages user creation and profile setup.
--> Validation and Processing: The serializer ensures data integrity by validating the user input and facilitating the creation of user records in the database.

3.  Views:

This document provides an overview of the functionalities offered by your Google Books Django project's APIs. It details the functionalities of each API endpoint along with the expected request data format and the response format.

Here's a breakdown of the functionalities offered by each class:

* **BooksConfigurations:
    * **GET /books/search** - Searches for books based on search key and search type (keyword, title, author, categories). 
        * Request:
            * `search_key`: (Required) The keyword or phrase to search for.
            * `search_type`: (Required) One of "keyword", "title", "author", or "categories".
        * Response:
            * A list of book details containing information like title, author, categories, ISBN, cover image URL, publication date, description, recommended by count, comments count, average rating.
    * **POST /books** - Creates a new book entry.
        * Request:
            * `title`: (Required) Title of the book (string).
            * `author_id`: (Required) ID of the author (integer).
            * `cover_pic`: (Optional) URL of the book cover image (string).
            * `categories`: (Required) Categories of the book (string, comma-separated).
            * `isbn`: (Optional) ISBN number of the book (string).
            * `description`: (Required) Description of the book (string).
            * `publisheddate`: (Optional) Publication date of the book in YYYY-MM-DD format (string).
        * Response:
            * Message indicating success or failure and details of the created book entry (if successful).
    * **PUT /books** - Updates an existing book entry.
        * Request:
            * `book_id`: (Required) ID of the book to be updated (integer).
            * Similar structure to POST request with additional `author_id` field (all fields are optional).
        * Response:
            * Message indicating success or failure and details of the updated book entry (if successful).
    * **DELETE /books** - Deletes an existing book entry.
        * Request:
            * `book_id`: (Required) ID of the book to be deleted (integer).
        * Response:
            * Message indicating success or failure.

* **BookSearchKeywordList:**
    * **GET /books/search/key-types** - Returns a list of valid search type options (keyword, title, author, categories).
        * Response:
            * List of strings representing valid search types.

* **AuthorConfigurations:**
    * **GET /authors** - Searches for authors based on author name. Partial matches are considered.
        * Request:
            * `author_name`: (Required) Name of the author (string).
        * Response:
            * List of author details containing author ID and full name.
    * **POST /authors** - Creates a new author entry.
        * Request:
            * `full_name`: (Required) Full name of the author (string).
        * Response:
            * Message indicating success or failure. 
    * **PUT /authors** - Updates an existing author entry.
        * Request:
            * `author_id`: (Required) ID of the author to be updated (integer).
            * `full_name`: (Required) Updated full name of the author (string).
        * Response:
            * Message indicating success or failure.
    * **DELETE /authors** - Deletes an existing author entry.
        * Request:
            * `author_id`: (Required) ID of the author to be deleted (integer).
        * Response:
            * Message indicating success or failure.

* **RecommendationConfigurations:**
    * **GET /recommendations** - Retrieves recommendations made by a user.
        * Request:
            * `user_id`: (Required) ID of the user (integer).
        * Response:
            * List of recommendations containing book details (title, author, categories, etc.) and the recommendation note (if provided).
    * **POST /recommendations** - Creates a new book recommendation for a user.
        * Request:
            * `user_id`: (Required) ID of the user making the recommendation (integer).
            * `book_id`: (Required) ID of the book being recommended (integer).
            * `note`: (Optional) Note about the recommendation (string).
        * Response:
            * Message indicating success or failure. 
    * **DELETE /recommendations** - Deletes a user's recommendation.
        * Request:
            * `recommendation_id`: (Required




