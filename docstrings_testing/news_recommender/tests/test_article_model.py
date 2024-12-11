from contextlib import contextmanager
import re
import sqlite3
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def mock_db_connection(): #implemented solely for testing download_article
    """Fixture that mocks the database connection and cursor."""
    # Create a mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Mock the connection's cursor method to return the mock cursor
    mock_conn.cursor.return_value = mock_cursor

    # Return the mock connection and cursor as a tuple
    yield mock_conn, mock_cursor

    # Clean up after the test
    mock_conn.close()

from news_recommender.models.article_model import (
    Article,
    create_article,
    clear_catalog,
    delete_article,
    get_article_by_id,
    get_article_by_compound_key,
    get_all_articles,
    update_read_count,
    download_article
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("news_recommender.models.article_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_article(mock_cursor):
    """Test creating a new article in the catalog."""

    # Call the function to create a new article
    create_article(id=1, name="Name", author="Article Author", title="How pigeons fly",
                   publishedAt="2024-12-05T19:58:30Z", url="https://newsapi.org/v2/everything?q=tesla&from=2024-11-06&sortBy=publishedAt&apiKey=e616acff8a674cfc8ba4648026e85f1d", 
                   content="Smaller public companies are taking a leaf out of MicroStrategys radical playbook by adopting a Bitcoin treasury strategy. And one is even adding in the Ripple-linked XRP, too.\r\nThe latest is auto fi… ")

    expected_query = normalize_whitespace("""
        INSERT INTO articles (id, name, author, title, url, content, publishedAt)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    create_article(id = 1, name="Name", author="Article Author", title="How pigeons fly",
                   
                   url="https://newsapi.org/v2/everything?q=tesla&from=2024-11-06&sortBy=publishedAt&apiKey=e616acff8a674cfc8ba4648026e85f1d", 
                   content="Smaller public companies are taking a leaf out of MicroStrategys radical playbook by adopting a Bitcoin treasury strategy. And one is even adding in the Ripple-linked XRP, too.\r\nThe latest is auto fi… ", 
                   publishedAt="2024-12-05T19:58:30Z")
    expected_arguments = (1, "Name", "Article Author", "How pigeons fly", 
                          "https://newsapi.org/v2/everything?q=tesla&from=2024-11-06&sortBy=publishedAt&apiKey=e616acff8a674cfc8ba4648026e85f1d", 
                          "Smaller public companies are taking a leaf out of MicroStrategys radical playbook by adopting a Bitcoin treasury strategy. And one is even adding in the Ripple-linked XRP, too.\r\nThe latest is auto fi… ",
                          "2024-12-05T19:58:30Z")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_article_duplicate(mock_cursor):
    """Test creating a article with a duplicate name, title, and url (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: article.name, article.title, article.url")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match=r"^Article with writer 'Name', title 'How pigeons fly', and url https:\/\/newsapi\.org\/v2\/everything\?q=tesla&from=2024-11-06&sortBy=publishedAt&apiKey=e616acff8a674cfc8ba4648026e85f1d already exists\.$"):
        create_article(id=1, name="Name", author="Article Author", title="How pigeons fly",
                   
                   url="https://newsapi.org/v2/everything?q=tesla&from=2024-11-06&sortBy=publishedAt&apiKey=e616acff8a674cfc8ba4648026e85f1d", 
                   content="Smaller public companies are taking a leaf out of MicroStrategys radical playbook by adopting a Bitcoin treasury strategy. And one is even adding in the Ripple-linked XRP, too.\r\nThe latest is auto fi… ", 
                   publishedAt="2024-12-05T19:58:30Z")
                   


def test_create_article_invalid_date():
    """Test error when trying to create a article with an invalid year (e.g., less than 1900 or non-integer)."""

    # Attempt to create a article with a year less than 1900
    with pytest.raises(ValueError, match=r"Invalid year provided: 1899 \(must be an integer greater than or equal to 1900\)."):
        create_article(1, "Article", "Author", "Title", "url", "content", '1899-12-05T19:58:30Z')

    # Attempt to create a article with a non-integer year
    with pytest.raises(ValueError, match=r"Expected a string for publishedAt, but got <class 'int'>"):
        create_article(1, "Article", "Author", "Title", "url", "content", 1899)

def test_delete_article(mock_cursor):
    """Test soft deleting a article from the catalog by article ID."""

    # Simulate that the article exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_article function
    delete_article(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM articles WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE articles SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_article_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent article."""

    # Simulate that no article exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent article
    with pytest.raises(ValueError, match="Article with ID 999 not found"):
        delete_article(999)

def test_delete_article_already_deleted(mock_cursor):
    """Test error when trying to delete a article that's already marked as deleted."""

    # Simulate that the article exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a article that's already been deleted
    with pytest.raises(ValueError, match="Article with ID 999 has already been deleted"):
        delete_article(999)

def test_clear_catalog(mock_cursor, mocker):
    """Test clearing the entire article catalog (removes all articles)."""

    # Mock the file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_article_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))

    # Call the clear_database function
    clear_catalog()

    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/create_article_table.sql', 'r')

    # Verify that the correct SQL script was executed
    mock_cursor.executescript.assert_called_once()


######################################################
#
#    Get Article
#
######################################################

def test_get_article_by_id(mock_cursor):
    # Simulate that the article exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Name 1", "Author 1", "Title 1", "URL 1", "Content 1", "2024-1", 0, False)

    # Call the function and check the result
    result = get_article_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Article(1, "Name 1", "Author 1", "Title 1", "URL 1", "Content 1", "2024-1")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, name, author, title, url, content, publishedAt, deleted FROM articles WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_article_by_id_bad_id(mock_cursor):
    # Simulate that no article exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the article is not found
    with pytest.raises(ValueError, match="Article with ID 999 not found"):
        get_article_by_id(999)

def test_get_article_by_compound_key(mock_cursor):
    # Simulate that the article exists (name = "Name", title = "Title", url = URL)
    mock_cursor.fetchone.return_value = (1, "Name", "Author", "Title", "URL", "Content", "2024-16-39133EDD", 0, False)

    # Call the function and check the result
    result = get_article_by_compound_key("Name", "Title", "URL")

    # Expected result based on the simulated fetchone return value
    expected_result = Article(1, "Name", "Author", "Title", "URL", "Content", "2024-16-39133EDD")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, name, author, title, url, content, publishedAt, deleted FROM articles WHERE name = ? AND title = ? AND url = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Name", "Title", "URL")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_all_articles(mock_cursor):
    """Test retrieving all articles that are not marked as deleted."""

    # Simulate that there are multiple articles in the database
    mock_cursor.fetchall.return_value = [
        (1, "Name 1", "Author 1", "Title 1", "URL 1", "Content 1", "2024-1", 0, False),
        (2, "Name 2", "Author 2", "Title 2", "URL 2", "Content 2", "2024-2", 1, False),
        (3, "Name 3", "Author 3", "Title 3", "URL 3", "Content 3", "2024-3", 2, False)
    ]

    # Call the get_all_articles function
    articles = get_all_articles()

    # Ensure the results match the expected output
    expected_result = [
    {"id": 1, "name": "Name 1", "author": "Author 1", "title": "Title 1", "url": "URL 1", "content": "Content 1", "publishedAt": "2024-1"},
    {"id": 2, "name": "Name 2", "author": "Author 2", "title": "Title 2", "url": "URL 2", "content": "Content 2", "publishedAt": "2024-2"},
    {"id": 3, "name": "Name 3", "author": "Author 3", "title": "Title 3", "url": "URL 3", "content": "Content 3", "publishedAt": "2024-3"}
    ]

    assert articles == expected_result, f"Expected {expected_result}, but got {articles}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, name, author, title, url, content, publishedAt, deleted
        FROM articles
        WHERE deleted = FALSE
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_all_articles_empty_catalog(mock_cursor, caplog):
    """Test that retrieving all articles returns an empty list when the catalog is empty and logs a warning."""

    # Simulate that the catalog is empty (no articles)
    mock_cursor.fetchall.return_value = []

    # Call the get_all_articles function
    result = get_all_articles()

    # Ensure the result is an empty list
    assert result == [], f"Expected empty list, but got {result}"

    # Ensure that a warning was logged
    assert "The article catalog is empty." in caplog.text, "Expected warning about empty catalog not found in logs."

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, name, author, title, url, content, publishedAt, deleted FROM articles WHERE deleted = FALSE")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
'''
def test_get_all_articles_ordered_by_play_count(mock_cursor):
    """Test retrieving all articles ordered by play count."""

    # Simulate that there are multiple articles in the database
    mock_cursor.fetchall.return_value = [
        (2, "Artist B", "article B", 2021, "Pop", 180, 20),
        (1, "Artist A", "article A", 2020, "Rock", 210, 10),
        (3, "Artist C", "article C", 2022, "Jazz", 200, 5)
    ]

    # Call the get_all_articles function with sort_by_play_count = True
    articles = get_all_articles(sort_by_play_count=True)

    # Ensure the results are sorted by play count
    expected_result = [
        {"id": 2, "artist": "Artist B", "title": "article B", "year": 2021, "genre": "Pop", "duration": 180, "play_count": 20},
        {"id": 1, "artist": "Artist A", "title": "article A", "year": 2020, "genre": "Rock", "duration": 210, "play_count": 10},
        {"id": 3, "artist": "Artist C", "title": "article C", "year": 2022, "genre": "Jazz", "duration": 200, "play_count": 5}
    ]

    assert articles == expected_result, f"Expected {expected_result}, but got {articles}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, artist, title, year, genre, duration, play_count
        FROM articles
        WHERE deleted = FALSE
        ORDER BY play_count DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."
'''

def test_update_read_count(mock_cursor):
    """Test updating the play count of a article."""

    # Simulate that the article exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_read_count function with a sample article ID
    article_id = 1
    update_read_count(article_id)

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE articles SET read_count = read_count + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (article ID)
    expected_arguments = (article_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

### Test for Updating a Deleted article:
def test_update_read_count_deleted_article(mock_cursor):
    """Test error when trying to update play count for a deleted article."""

    # Simulate that the article exists but is marked as deleted (id = 1)
    mock_cursor.fetchone.return_value = [True]

    # Expect a ValueError when attempting to update a deleted article
    with pytest.raises(ValueError, match="Article with ID 1 has been deleted"):
        update_read_count(1)

    # Ensure that no SQL query for updating play count was executed
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM articles WHERE id = ?", (1,))

def test_download_article(mock_db_connection):
    """Test downloading an article and saving it to the database."""
    # Mock data returned by get_articles_info
    mock_article_data = {
        "author": "Paresh Dave",
        "title": "The Future of Online Privacy Hinges on Thousands of New Jersey Cops",
        "content": "LexisNexis spokesperson Paul Eckloff disputes that freezing was an overreach. The company deemed that step as necessary to honor the requests submitted by Atlas users to not disclose their data. This… [+2458 chars]",
        "url": "https://www.wired.com/story/daniels-law-new-jersey-online-privacy-matt-adkisson-atlas-lawsuits/",
        "publishedAt": "2024-11-25T11:00:00Z"
    }

    # Mock the get_articles_info function
    with patch("news_recommender.models.article_model.get_articles_info", return_value=mock_article_data), \
         patch("news_recommender.models.article_model.create_article") as mock_create_article, \
         patch("news_recommender.models.article_model.get_article_by_id") as mock_get_article_by_id:
        
        # Call the function under test
        download_article("Privacy Revolution")

        # Verify create_article was called with correct arguments
        expected_article_id = hash(
            mock_article_data["title"] + mock_article_data["author"] + mock_article_data["url"]
        )
        mock_create_article.assert_called_once_with(
            id=expected_article_id,
            name="Privacy Revolution",
            author=mock_article_data["author"],
            title=mock_article_data["title"],
            url=mock_article_data["url"],
            content=mock_article_data["content"],
            publishedAt=mock_article_data["publishedAt"]
        )

        # Simulate the database returning the created article
        mock_get_article_by_id.return_value = Article(
            id=expected_article_id,
            name="Privacy Revolution",
            author=mock_article_data["author"],
            title=mock_article_data["title"],
            url=mock_article_data["url"],
            content=mock_article_data["content"],
            publishedAt=mock_article_data["publishedAt"]
        )

        # Verify the article was stored correctly
        stored_article = mock_get_article_by_id(expected_article_id)
        assert stored_article.name == "Privacy Revolution"
        assert stored_article.author == mock_article_data["author"]
        assert stored_article.title == mock_article_data["title"]
        assert stored_article.url == mock_article_data["url"]
        assert stored_article.content == mock_article_data["content"]
        assert stored_article.publishedAt == mock_article_data["publishedAt"]