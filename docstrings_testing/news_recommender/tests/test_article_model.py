from contextlib import contextmanager
import re
import sqlite3

import pytest

from news_recommender.models.article_model import (
    Article,
    create_article,
    clear_catalog,
    delete_article,
    get_article_by_id,
    get_article_by_compound_key,
    get_all_articles,
    #get_random_song,
    update_read_count
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
    """Test creating a new song in the catalog."""

    # Call the function to create a new song
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
    """Test creating a song with a duplicate artist, title, and year (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: article.name, article.title, article.url")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match=r"^Article with writer 'Name', title 'How pigeons fly', and url https:\/\/newsapi\.org\/v2\/everything\?q=tesla&from=2024-11-06&sortBy=publishedAt&apiKey=e616acff8a674cfc8ba4648026e85f1d already exists\.$"):
        create_article(id=1, name="Name", author="Article Author", title="How pigeons fly",
                   
                   url="https://newsapi.org/v2/everything?q=tesla&from=2024-11-06&sortBy=publishedAt&apiKey=e616acff8a674cfc8ba4648026e85f1d", 
                   content="Smaller public companies are taking a leaf out of MicroStrategys radical playbook by adopting a Bitcoin treasury strategy. And one is even adding in the Ripple-linked XRP, too.\r\nThe latest is auto fi… ", 
                   publishedAt="2024-12-05T19:58:30Z")
                   
'''

def test_create_song_invalid_year():
    """Test error when trying to create a song with an invalid year (e.g., less than 1900 or non-integer)."""

    # Attempt to create a song with a year less than 1900
    with pytest.raises(ValueError, match="Invalid year provided: 1899 (must be an integer greater than or equal to 1900)."):
        create_song(artist="Artist Name", title="Song Title", year=1899, genre="Pop", duration=180)

    # Attempt to create a song with a non-integer year
    with pytest.raises(ValueError, match="Invalid year provided: invalid (must be an integer greater than or equal to 1900)."):
        create_song(artist="Artist Name", title="Song Title", year="invalid", genre="Pop", duration=180)
'''
def test_delete_song(mock_cursor):
    """Test soft deleting a song from the catalog by song ID."""

    # Simulate that the song exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_song function
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

def test_delete_song_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent song."""

    # Simulate that no song exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent song
    with pytest.raises(ValueError, match="Article with ID 999 not found"):
        delete_article(999)

def test_delete_song_already_deleted(mock_cursor):
    """Test error when trying to delete a song that's already marked as deleted."""

    # Simulate that the song exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a song that's already been deleted
    with pytest.raises(ValueError, match="Article with ID 999 has already been deleted"):
        delete_article(999)

def test_clear_catalog(mock_cursor, mocker):
    """Test clearing the entire song catalog (removes all songs)."""

    # Mock the file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_song_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))

    # Call the clear_database function
    clear_catalog()

    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/create_song_table.sql', 'r')

    # Verify that the correct SQL script was executed
    mock_cursor.executescript.assert_called_once()


######################################################
#
#    Get Song
#
######################################################

def test_get_article_by_id(mock_cursor):
    # Simulate that the song exists (id = 1)
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
    # Simulate that no song exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the song is not found
    with pytest.raises(ValueError, match="Article with ID 999 not found"):
        get_article_by_id(999)

def test_get_article_by_compound_key(mock_cursor):
    # Simulate that the song exists (artist = "Artist Name", title = "Song Title", year = 2022)
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
    """Test retrieving all songs that are not marked as deleted."""

    # Simulate that there are multiple songs in the database
    mock_cursor.fetchall.return_value = [
        (1, "Name 1", "Author 1", "Title 1", "URL 1", "Content 1", "2024-1", 0, False),
        (2, "Name 2", "Author 2", "Title 2", "URL 2", "Content 2", "2024-2", 1, False),
        (3, "Name 3", "Author 3", "Title 3", "URL 3", "Content 3", "2024-3", 2, False)
    ]

    # Call the get_all_songs function
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
    """Test that retrieving all songs returns an empty list when the catalog is empty and logs a warning."""

    # Simulate that the catalog is empty (no songs)
    mock_cursor.fetchall.return_value = []

    # Call the get_all_songs function
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
def test_get_all_songs_ordered_by_play_count(mock_cursor):
    """Test retrieving all songs ordered by play count."""

    # Simulate that there are multiple songs in the database
    mock_cursor.fetchall.return_value = [
        (2, "Artist B", "Song B", 2021, "Pop", 180, 20),
        (1, "Artist A", "Song A", 2020, "Rock", 210, 10),
        (3, "Artist C", "Song C", 2022, "Jazz", 200, 5)
    ]

    # Call the get_all_songs function with sort_by_play_count = True
    songs = get_all_songs(sort_by_play_count=True)

    # Ensure the results are sorted by play count
    expected_result = [
        {"id": 2, "artist": "Artist B", "title": "Song B", "year": 2021, "genre": "Pop", "duration": 180, "play_count": 20},
        {"id": 1, "artist": "Artist A", "title": "Song A", "year": 2020, "genre": "Rock", "duration": 210, "play_count": 10},
        {"id": 3, "artist": "Artist C", "title": "Song C", "year": 2022, "genre": "Jazz", "duration": 200, "play_count": 5}
    ]

    assert songs == expected_result, f"Expected {expected_result}, but got {songs}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, artist, title, year, genre, duration, play_count
        FROM songs
        WHERE deleted = FALSE
        ORDER BY play_count DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_random_song(mock_cursor, mocker):
    """Test retrieving a random song from the catalog."""

    # Simulate that there are multiple songs in the database
    mock_cursor.fetchall.return_value = [
        (1, "Artist A", "Song A", 2020, "Rock", 210, 10),
        (2, "Artist B", "Song B", 2021, "Pop", 180, 20),
        (3, "Artist C", "Song C", 2022, "Jazz", 200, 5)
    ]

    # Mock random number generation to return the 2nd song
    mock_random = mocker.patch("music_collection.models.song_model.get_random", return_value=2)

    # Call the get_random_song method
    result = get_random_song()

    # Expected result based on the mock random number and fetchall return value
    expected_result = Song(2, "Artist B", "Song B", 2021, "Pop", 180)

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure that the random number was called with the correct number of songs
    mock_random.assert_called_once_with(3)

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, artist, title, year, genre, duration, play_count FROM songs WHERE deleted = FALSE")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_random_song_empty_catalog(mock_cursor, mocker):
    """Test retrieving a random song when the catalog is empty."""

    # Simulate that the catalog is empty
    mock_cursor.fetchall.return_value = []

    # Expect a ValueError to be raised when calling get_random_song with an empty catalog
    with pytest.raises(ValueError, match="The song catalog is empty"):
        get_random_song()

    # Ensure that the random number was not called since there are no songs
    mocker.patch("music_collection.models.song_model.get_random").assert_not_called()

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, artist, title, year, genre, duration, play_count FROM songs WHERE deleted = FALSE")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
'''

def test_update_read_count(mock_cursor):
    """Test updating the play count of a song."""

    # Simulate that the song exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_read_count function with a sample song ID
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

    # Assert that the SQL query was executed with the correct arguments (song ID)
    expected_arguments = (article_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

### Test for Updating a Deleted Song:
def test_update_read_count_deleted_article(mock_cursor):
    """Test error when trying to update play count for a deleted song."""

    # Simulate that the song exists but is marked as deleted (id = 1)
    mock_cursor.fetchone.return_value = [True]

    # Expect a ValueError when attempting to update a deleted song
    with pytest.raises(ValueError, match="Article with ID 1 has been deleted"):
        update_read_count(1)

    # Ensure that no SQL query for updating play count was executed
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM articles WHERE id = ?", (1,))
