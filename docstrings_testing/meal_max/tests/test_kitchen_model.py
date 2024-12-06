from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
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

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_meal(mock_cursor):
    """Test creating a new song in the catalog."""

    # Call the function to create a new song
    create_meal(meal="Pancakes", cuisine="**", price=12.20, difficulty='MED')

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Pancakes", "**", 12.20, 'MED')
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_create_duplicate_meal(mock_cursor):
    """Test attempting to create a duplicate meal raises an error."""
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed")
    with pytest.raises(ValueError, match="Meal with name 'Meal 1' already exists"):
        create_meal(meal="Meal 1", cuisine="Cuisine 1", price=10.0, difficulty="LOW")


def test_create_meal_invalid_price():
    """Test error when trying to create a song with an invalid duration (e.g., negative duration)"""

    # Attempt to create a song with a negative duration
    with pytest.raises(ValueError, match="Invalid price: -20.0. Price must be a positive number."):
        create_meal(meal="Meal 1", cuisine="Cuisine 1", price=-20.0, difficulty="LOW")

    # Attempt to create a song with a non-integer duration
    with pytest.raises(ValueError, match="Invalid difficulty level: invalid. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Meal 1", cuisine="Cuisine 1", price=10.0, difficulty="invalid")

def test_meal_invalid_difficulty():
    """Test error when trying to create a song with an invalid year (e.g., less than 1900 or non-integer)."""

    with pytest.raises(ValueError, match="Invalid difficulty level: invalid. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Meal 1", cuisine="Cuisine 1", price=10.0, difficulty="invalid")

def test_delete_meal(mock_cursor):
    """Test soft deleting a song from the catalog by song ID."""

    # Simulate that the song exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_song function
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

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

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent song."""

    # Simulate that no song exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent song
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a song that's already marked as deleted."""

    # Simulate that the song exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a song that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)

def test_clear_catalog(mock_cursor, mocker):

    # Mock the file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))

    # Call the clear_database function
    clear_meals()

    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')

    # Verify that the correct SQL script was executed
    mock_cursor.executescript.assert_called_once()


######################################################
#
#    Get Meal
#
######################################################

def test_get_meal_by_id(mock_cursor):
    # Simulate that the song exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Meal 1", "Cuisine 1", 20.0, "LOW", False)

    # Call the function and check the result
    result = get_meal_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Meal 1", "Cuisine 1", 20.0, "LOW")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_id_bad_id(mock_cursor):
    # Simulate that no song exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the song is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_update_meal_stats(mock_cursor):
    """Test updating the play count of a song."""

    # Simulate that the song exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_play_count function with a sample song ID
    meal_id = 1
    update_meal_stats(meal_id, 'win')

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (song ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

### Test for Updating a Deleted Song:
def test_get_leaderboard(mock_cursor):

    # Simulate that there are multiple songs in the database
    mock_cursor.fetchall.return_value = [
        (1, "Meal 1", "Cuisine 1", 20.0, "LOW", 3, 1, .33),
        (2, "Meal 2", "Cuisine 2", 20.0, "MED", 3, 2, .66)
    ]

    # Call the get_all_songs function with sort_by_play_count = True
    leaderboard = get_leaderboard(sort_by="wins")

    # Ensure the results are sorted by play count
    expected_result = [
 {'id': 1, 'meal': 'Meal 1', 'cuisine': 'Cuisine 1', 'price': 20.0, 'difficulty': 'LOW', 'battles': 3, 'wins': 1, 'win_pct': 33.0},
 {'id': 2, 'meal': 'Meal 2', 'cuisine': 'Cuisine 2', 'price': 20.0, 'difficulty': 'MED', 'battles': 3, 'wins': 2, 'win_pct': 66.0}
    ]

    assert leaderboard == expected_result, f"Expected {expected_result}, but got {leaderboard}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles)
        AS win_pct 
        FROM meals
        WHERE deleted = false
        AND battles > 0 ORDER
        BY wins
        DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_meal_by_name(mock_cursor):
    # Simulate that the song exists (artist = "Artist Name", title = "Song Title", year = 2022)
    mock_cursor.fetchone.return_value = (1, "Meal 1", "Cuisine 1", 20.0, "LOW", False)

    # Call the function and check the result
    result = get_meal_by_name("Meal 1")

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Meal 1", "Cuisine 1", 20.0, "LOW")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal 1",)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
