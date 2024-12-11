This is the README.md file for our CS 411 Project containing a high level overview of the project. 

Contributors: Alexander Cobb, Brian Sull, Ryan Hwang

At a high level, our application seeks to provide a user new and recommended articles based on previous searches. For each specific user, this application will track and store articles that user has retrieved. After a given amount of articles that the user has read, the user can request for our application to automatically recommend articles to read in the future, just like how YouTube recommends videos based on viewing history. 

In a world where current events are widely available, it is important for all demographics - students, teachers, employees, managers, elderly - to stay in touch with the changing landscape. Thus, by using our application, people will easily have articles that are personalized and credible every morning. 

To Run:
    cd news_recommender
    ./setup_venv.sh
    source news_recommender_venv/bin/activate
    ./run_docker.sh
    python3 app.py

Routes: 

Route: /create-account
    ● Request Type: POST
    ● Purpose: Creates a new user account with a username and password.
    ● Request Body:
        ○ username (String): User's chosen username.
        ○ password (String): User's chosen password.
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "message": "Account created successfully" }
    ● Example Request:
        {
        "username": "newuser123",
        "password": "securepassword"
        }
    ● Example Response:
        {
        "message": "Account created successfully",
        "status": "2
        }

Route: /login
    ● Request Type: GET
    ● Purpose: Logs in user based on a password that matches the password created when the account was created.
    ● Request Body:
        ○ username (String): Entered username.
        ○ password (String): Entered password.
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "message": "Login successful!" }
    ● Example Request:
        {
        "username": "newuser123",
        "password": "passwordpassword"
        }
    ● Example Response:
        {
        "message": "Login successful",
        "status": "2
        }

Route: /update-password
    ● Request Type: POST
    ● Purpose: Creates a new password for a given username.
    ● Request Body:
        ○ username (String): User's username.
        ○ password (String): New password.
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "message": "Password updated successfully" }
    ● Example Request:
        {
        "username": "newuser123",
        "password": "newpassword"
        }
    ● Example Response:
        {
        "message": "Password updated successfully",
        "status": "2
        }

Route: /get-unique-article
    ● Request Type: GET
    ● Purpose: User reads a unique article, and this history is recorded in the system.
    ● Request Body:
        ○ title (String): Title of article read,
        ○ author (String): Author of article,
        ○ date (String): Date article was written,
        ○ title (String): Title of article read,
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "message": "Article read" }
    ● Example Request:
        {
        "title": "Why the George Sherman Union needs new food options",
        "author": "BU Today"
        "date_published": 12-05-2024
        }
    ● Example Response:
        {
        "message": "Article read successfully",
        "status": "2
        }

Route: /get-articles-by-author
    ● Request Type: GET
    ● Purpose: User searches for articles based on the author.
    ● Request Body:
        ○ author (String): Author of article,
        ○ size (int): Number of articles to retrieve,
        ○ sort_most_recent (boolean): Boolean if user wants most recent articles or randomized,
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "message": Articles retrieved successfully,
                            "Articles": [{ "Title 1", "Title 2", "Title 3" }]}
    ● Example Request:
        {
        "author": "BU Today",
        "size": 2,
        "sort_most_recent": True
        }
    ● Example Response:
        {
        "message": "Articles retrieved successfully",
        "Articles": "Basho is severely overrated. Here's why.", "Halal Shack under investigation for food poisoning"
        "status": 2
        }

Route: /get-articles-written-on-date
    ● Request Type: GET
    ● Purpose: User searches for articles written on a date.
    ● Request Body:
        ○ datePublished (String):  Date of article publication,
        ○ size (int):  Number of articles to retrieve
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "message": Articles retrieved successfully,
                            "Articles": [{ "Title 1", "Title 2", "Title 3" }]}
    ● Example Request:
        {
        "author": "BU Today",
        "size": 2,
        "sort_most_recent": True
        }
    ● Example Response:
        {
        "message": "Articles retrieved successfully",
        "Articles": "Halal Shack reportedly adds food coloring and additive chemicals to its bowls.", "Halal Shack under investigation for food poisoning"
        "status": 2
        }

Route: /favorite-article
    ● Request Type: GET
    ● Purpose: User retrieves favorite, or most viewed/read, article.
    ● Request Body:
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "message": Article retrieved successfully,
                            "Article": "Title 1"}
    ● Example Request:
        {
        }
    ● Example Response:
        {
        "message": "Article retrieved successfully",
        "Article": "Halal Shack under investigation for food poisoning"
        "status": 2
        }

Route: /favorite-author
    ● Request Type: GET
    ● Purpose: User retrieves favorite, or most viewed/read, author.
    ● Request Body:
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "message": Author retrieved successfully,
                            "Author": "Name 1"}
    ● Example Request:
        {
        }
    ● Example Response:
        {
        "message": "Author retrieved successfully",
        "Author": "BU Today"
        "status": 2
        }

Route: /save-article
    ● Request Type: POST
    ● Purpose: User saves an article.
    ● Request Body:
        {
            "title": Title of article,
            "author": Author of article,
            }
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "message": Article retrieved successfully
                                }   
    ● Example Request:
        {
            "title": "Halal Shack under investigation for food poisoning",
            "author": "BU Today"
        }
    ● Example Response:
        {
        "message": "Article saved successfully",
        "status": 2
        }

Route: /delete-article-from-saved
    ● Request Type: DELETE
    ● Purpose: User saves an article.
    ● Request Body:
        {
            "title": Title of article,
            "author": Author of article,
            }
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "message": Article deleted successfully
                                }   
    ● Example Request:
        {
            "title": "Halal Shack under investigation for food poisoning",
            "author": "BU Today"
        }
    ● Example Response:
        {
        "message": "Article deleted successfully",
        "status": 2
        }

Route: /recommend-articles
    ● Request Type: GET
    ● Purpose: Application recommends articles to user based on saved preferences
    ● Request Body:
        {
            "size": Number of recommended articles,
            }
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "message": Articles retrieved successfully,
                         "Article": "Title 1",
                         "Author": "Author 1"
                                }   
    ● Example Request:
        {
            "size": 2
        }
    ● Example Response:
        {
        "message": "Articles retrieved successfully",
        "Articles": "Basho is severely overrated. Here's why.", "Halal Shack under investigation for food poisoning",
        "Author": "BU Today", "The New York Times",
        "status": 2
        }


