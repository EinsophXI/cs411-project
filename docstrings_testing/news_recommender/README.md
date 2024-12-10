This is the README.md file for our CS 411 Project containing a high level overview of the project. 

Contributors: Alexander Cobb, Brian Sull, Ryan Hwang

At a high level, our application seeks to provide a user new and recommended articles based on previous searches. For each specific user, this application will track and store articles that user has retrieved. After a given amount of articles that the user has read, the user can request for our application to automatically recommend articles to read in the future, just like how YouTube recommends videos based on viewing history. 

In a world where current events are widely available, it is important for all demographics - students, teachers, employees, managers, elderly - to stay in touch with the changing landscape. Thus, by using our application, people will easily have articles that are personalized and credible every morning. 

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
    ● Request Type: POST
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

Route: /read-current-article
    ● Request Type: POST
    ● Purpose: User reads the current article, and this history is recorded in the system.
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "status": "success"}
    ● Example Request:
    ● Example Response:
        {
        "status": "success"
        }

Route: /read-entire-journal 
    ● Request Type: POST
    ● Purpose: User reads the entire journal, and this history is recorded in the system.
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "status": "success"}
    ● Example Request:
    ● Example Response:
        {
        "status": "success"
        }


Route: /create-article
    ● Request Type: POST
    ● Purpose: User creates an article using request criteria
    ● Request Body:
        ○ name (String): Name of article,
        ○ author (String): Author of article,
        ○ title (String): Title of article,
        ○ url (String): URL of article,
        ○ content (String): Content of article,
        ○ publishedAt (String): Date article was published.
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "message": Articles retrieved successfully,
                            "Article Name": article_name}
    ● Example Request:
        {
        "name": "Basho is severely overrated. Here's why."
        "author": "BU Today",
        "title": "Basho is severely overrated. Here's why."
        "url": www.linkedin.com
        "content": Lorem Ipsum
        "publishedAt": "22-11-2023"
        }
    ● Example Response:
        {
        "message": "Articles retrieved successfully",
        "Article Name": "Basho is severely overrated. Here's why."
        }

Route: /get-article-by-id
    ● Request Type: GET
    ● Purpose: User searches for articles based on the article ID.
    ● Request Body:
        ○ article id (int): ID of article
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "status": success,
                            "article name": "Name 1"}
    ● Example Request:
        {
        "article id": 5
        }
    ● Example Response:
        {
        "status": "success",
        "article name": "Halal Shack under investigation for food poisoning"
        }

Route: /get-current-article
    ● Request Type: GET
    ● Purpose: User retrieves current article in journal
    ● Request Body:
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "status": success,
                            "article name": "Name 1",
                            "article ID": "id 1",
                            "author": "author 1"}
    ● Example Request:
    ● Example Response:
        {
        "status": "success",
        "article name": "Halal Shack under investigation for food poisoning",
        "article ID": 55,
        "author": Martin Luther King Jr.
        }

Route: /get-journal-stats
    ● Request Type: GET
    ● Purpose: User retrieves journal statistics
    ● Request Body:
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "status": success,
                            "length": "length 1",
                            "duration": "duration 2"}
    ● Example Request:
    ● Example Response:
        {
        "status": "success",
        "length": 20,
        "duration": 3751
        }

Route: /swap-articles
    ● Request Type: POST
    ● Purpose: User swaps two articles in a journal
    ● Request Body:
        ○ article_id1 (int): ID of article 1
        ○ article_id2 (int): ID of article 2
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "status": success"}
    ● Example Request:
         {
            "article id1": 2,
            "article_id2": 355
        }
    ● Example Response:
        {
        "status": "success",
        }

Route: /delete-article
    ● Request Type: POST
    ● Purpose: User performs a soft delete on an article
    ● Request Body:
        ○ article_id (int): ID of article 
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "status": success"}
    ● Example Request:
         {
            "article_id": 25
        }
    ● Example Response:
        {
        "status": "success",
        }

Route: /remove-article-from-journal_id/<int:article_id>
    ● Request Type: POST
    ● Purpose: User deletes an article from the journal using article ID
    ● Request Body:
        ○ article_id (int): ID of article 
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "status": success"}
    ● Example Request:
         {
            "article_id": 25
        }
    ● Example Response:
        {
        "status": "success",
        }

Route: /remove-article-from-journal_num/<int:article_num>
    ● Request Type: POST
    ● Purpose: User deletes an article from the journal using article number
    ● Request Body:
        ○ article_id (int): ID of article 
    ● Response Format: JSON
        ○ Success Response Example:
            ■ Code: 200
            ■ Content: { "status": success"}
    ● Example Request:
         {
            "article_id": 25
        }
    ● Example Response:
        {
        "status": "success",
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


