from dataclasses import dataclass
import logging
import os
import sqlite3
import requests
import json
from unittest.mock import patch, MagicMock

from news_recommender.utils.article_utils import get_articles_info
from news_recommender.utils.logger import configure_logger
#from news_recommender.utils.article_utils import get_article
from news_recommender.utils.sql_utils import get_db_connection

logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Article:
    id: int
    name: str
    author: str
    title: str
    url: str
    content: str
    publishedAt: str  

    def __post_init__(self):
        if self.id <= 0:
            raise ValueError(f"ID must be greated than 0")
        if int(self.publishedAt.split('-')[0]) <= 1900:
            raise ValueError(f"Year must be greater than 1900, got {self.publishedAt}")


def create_article(id: int, name: str, author: str, title: str, url: str, content: str, publishedAt: str) -> None:
    """
    Creates a new song in the songs table.

    Args:
        artist (str): The artist's name.
        title (str): The song title.
        year (int): The year the song was released.
        genre (str): The song genre.
        duration (int): The duration of the song in seconds.

    Raises:
        ValueError: If year or duration are invalid.
        sqlite3.IntegrityError: If a song with the same compound key (artist, title, year) already exists.
        sqlite3.Error: For any other database errors.
    """
    # Validate the required fields
    if not isinstance(publishedAt, str) or int(publishedAt.split('-')[0]) < 1900:
        raise ValueError(f"Invalid year provided: {publishedAt.split('-')[0]} (must be an integer greater than or equal to 1900).")
    if not isinstance(content, str) or len(content) <= 0:
        raise ValueError(f"Invalid content length: {content} (must contain many letters).")

    try:
        # Use the context manager to handle the database connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO articles (id, name, author, title, url, content, publishedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id, name, author, title, url, content, publishedAt))
            conn.commit()

            logger.info("Article created successfully: %s - %s (%s)", author, title, url)

    except sqlite3.IntegrityError as e:
        logger.error("Article with author '%s', title '%s', and url %s already exists.", author, title, url)
        raise ValueError(f"Article with writer '{name}', title '{title}', and url {url} already exists.") from e
    except sqlite3.Error as e:
        logger.error("Database error while creating song: %s", str(e))
        raise sqlite3.Error(f"Database error: {str(e)}")

def clear_catalog() -> None:
    """
    Recreates the article table, effectively deleting all articles.

    Raises:
        sqlite3.Error: If any database error occurs.
    """
    try:
        with open(os.getenv("SQL_CREATE_TABLE_PATH", "/app/sql/create_article_table.sql"), "r") as fh:
            create_table_script = fh.read()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(create_table_script)
            conn.commit()

            logger.info("Catalog cleared successfully.")

    except sqlite3.Error as e:
        logger.error("Database error while clearing catalog: %s", str(e))
        raise e

def delete_article(article_id: int) -> None:
    """
    Soft deletes an article from the catalog by marking it as deleted.

    Args:
        song_id (int): The ID of the song to delete.

    Raises:
        ValueError: If the song with the given ID does not exist or is already marked as deleted.
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the song exists and if it's already deleted
            cursor.execute("SELECT deleted FROM articles WHERE id = ?", (article_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Article with ID %s has already been deleted", article_id)
                    raise ValueError(f"Article with ID {article_id} has already been deleted")
            except TypeError:
                logger.info("Article with ID %s not found", article_id)
                raise ValueError(f"Article with ID {article_id} not found")

            # Perform the soft delete by setting 'deleted' to TRUE
            cursor.execute("UPDATE articles SET deleted = TRUE WHERE id = ?", (article_id,))
            conn.commit()

            logger.info("Article with ID %s marked as deleted.", article_id)

    except sqlite3.Error as e:
        logger.error("Database error while deleting article: %s", str(e))
        raise e

def get_article_by_id(article_id: int) -> Article:
    """
    Retrieves an article from the catalog by its url.

    Args:
        song_id (int): The ID of the song to retrieve.

    Returns:
        Song: The Song object corresponding to the song_id.

    Raises:
        ValueError: If the song is not found or is marked as deleted.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve article with ID %s", article_id)
            cursor.execute("""
                SELECT id, name, author, title, url, content, publishedAt, deleted
                FROM articles
                WHERE id = ?
            """, (article_id,))
            row = cursor.fetchone()

            if row:
                if row[8]:  # deleted flag
                    logger.info("Article with ID %s has been deleted", article_id)
                    raise ValueError(f"Article with ID {article_id} has been deleted")
                logger.info("Article with ID %s found", article_id)
                return Article(id=row[0], name=row[1], author=row[2], title=row[3], url=row[4], content=row[5], publishedAt=row[6])
            else:
                logger.info("Article with ID %s not found", article_id)
                raise ValueError(f"Article with ID {article_id} not found")

    except sqlite3.Error as e:
        logger.error("Database error while retrieving song by ID %s: %s", article_id, str(e))
        raise e

def get_article_by_compound_key(name: str, title: str, url: str) -> Article:
    """
    Retrieves a song from the catalog by its compound key (name, author, url).

    Args:
        artist (str): The artist of the song.
        title (str): The title of the song.
        year (int): The year of the song.

    Returns:
        Song: The Song object corresponding to the compound key.

    Raises:
        ValueError: If the song is not found or is marked as deleted.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve song with artist '%s', title '%s', and year %s", name, title, url)
            cursor.execute("""
                SELECT id, name, author, title, url, content, publishedAt, deleted
                FROM articles
                WHERE name = ? AND title = ? AND url = ?
            """, (name, title, url,))
            row = cursor.fetchone()
            if row:
                if row[8]:  # deleted flag
                    logger.info("Article with name %s, title %s, and url %s has been deleted", name, title, url)
                    raise ValueError(f"Article with name {name}, title {title}, and url {url} has been deleted")
                logger.info("Article with name %s, title %s, and url %s has been found", name, title, url)
                return Article(id=row[0], name=row[1], author=row[2], title=row[3], url=row[4], content=row[5], publishedAt=row[6])
            else:
                logger.info("Song with artist '%s', title '%s', and url %s not found", name, title, url)
                raise ValueError(f"Song with artist '{name}', title '{title}', and year {url} not found")

    except sqlite3.Error as e:
        logger.error("Database error while retrieving song by compound key (artist '%s', title '%s', year %s): %s", name, title, url, str(e))
        raise e
    
def update_read_count(article_id: int) -> None:
    """
    Increments the read count of a article by article ID.

    Args:
        article_id (int): The ID of the article whose read count should be incremented.

    Raises:
        ValueError: If the article does not exist or is marked as deleted.
        sqlite3.Error: If there is a database error.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to update read count for article with ID %d", article_id)

            # Check if the song exists and if it's deleted
            cursor.execute("SELECT deleted FROM articles WHERE id = ?", (article_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Article with ID %d has been deleted", article_id)
                    raise ValueError(f"Article with ID {article_id} has been deleted")
            except TypeError:
                logger.info("Article with ID %d not found", article_id)
                raise ValueError(f"Article with ID {article_id} not found")

            # Increment the play count
            cursor.execute("UPDATE articles SET read_count = read_count + 1 WHERE id = ?", (article_id,))
            conn.commit()

            logger.info("Read count incremented for article with ID: %d", article_id)

    except sqlite3.Error as e:
        logger.error("Database error while updating read count for article with ID %d: %s", article_id, str(e))
        raise e


def get_all_articles(sort_by_id: bool = False) -> list[dict]:
    """
    Retrieves all articles that are not marked as deleted from the catalog.

    Args:
        sort_by_play_count (bool): If True, sort the songs by play count in descending order.

    Returns:
        list[dict]: A list of dictionaries representing all non-deleted songs with play_count.

    Logs:
        Warning: If the catalog is empty.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve all non-deleted songs from the catalog")

            # Determine the sort order based on the 'sort_by_play_count' flag
            query = """
                SELECT id, name, author, title, url, content, publishedAt, deleted
                FROM articles
                WHERE deleted = FALSE
            """
            if sort_by_id:
                query += " ORDER BY id DESC"

            cursor.execute(query)
            rows = cursor.fetchall()

            if not rows:
                logger.warning("The article catalog is empty.")
                return []

            articles = [
                {
                    "id": row[0],
                    "name": row[1],
                    "author": row[2],
                    "title": row[3],
                    "url": row[4],
                    "content": row[5],
                    "publishedAt": row[6]
                }
                for row in rows
            ]
            logger.info("Retrieved %d songs from the catalog", len(articles))
            return articles

    except sqlite3.Error as e:
        logger.error("Database error while retrieving all songs: %s", str(e))
        raise e
'''
def get_random_article() -> Article:
    """
    Retrieves a random song from the catalog.

    Returns:
        Song: A randomly selected Song object.

    Raises:
        ValueError: If the catalog is empty.
    """
    try:
        all_songs = get_all_songs()

        if not all_songs:
            logger.info("Cannot retrieve random song because the song catalog is empty.")
            raise ValueError("The song catalog is empty.")

        # Get a random index using the random.org API
        random_index = get_random(len(all_songs))
        logger.info("Random index selected: %d (total songs: %d)", random_index, len(all_songs))

        # Return the song at the random index, adjust for 0-based indexing
        song_data = all_songs[random_index - 1]
        return Song(
            id=song_data["id"],
            artist=song_data["artist"],
            title=song_data["title"],
            year=song_data["year"],
            genre=song_data["genre"],
            duration=song_data["duration"]
        )

    except Exception as e:
        logger.error("Error while retrieving random song: %s", str(e))
        raise e
'''
def add_note_to_content(article_id: int, text_to_add: str):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Step 1: Retrieve the content of the article by its id
            cursor.execute("SELECT content FROM articles WHERE id = ?", (article_id,))
            row = cursor.fetchone()
            
            if row:
                content = row[0]
                
                # Step 2: Check if the content contains the *& and &* markers
                start_marker = "*&"
                end_marker = "&*"
                
                start_idx = content.find(start_marker)
                end_idx = content.find(end_marker, start_idx + len(start_marker))
                
                if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                    # Step 3: Insert the new text within the markers if both markers are found
                    new_content = content[:start_idx + len(start_marker)] + text_to_add + content[end_idx:]
                    print("Markers found. Text inserted between them.")
                else:
                    # Step 4: If markers are missing, create them and add the text
                    new_content = start_marker + text_to_add + end_marker
                    print("Markers not found. Markers created and text added.")
                    
                # Step 5: Update the content back to the database
                cursor.execute("UPDATE articles SET content = ? WHERE id = ?", (new_content, article_id))
                print(f"Content updated successfully for article id {article_id}")
            else:
                print(f"Article with id {article_id} not found.")
    
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
def download_article(article_name: str) -> None:

    
    data = get_articles_info(article_name, 10)

    print(data)
    # Extract the first article
    try:
    # Convert `data` to a dictionary if it's in JSON format
        if isinstance(data, str):
            article = json.loads(data)  # Convert JSON string to a dictionary
        else:
            article = data  # Assume it's already a dictionary
        name = article_name
        author = article.get('author', 'Unknown Author')
        title = article.get('title', 'No Title')
        content = article.get('content', 'No Content')
        url = article.get('url', 'No URL')
        published_at = article.get('publishedAt', 'No Date')

        # Handle missing publication date
        if published_at == 'No Date':
            published_at = "1899-01-01"
        article_id = hash(title + author + url)

        # Add the article to the database
        logger.info("Adding article to database: %s", title)
        create_article(
            id=article_id,
            name=article_name,
            author=author,
            title=title,
            url=url,
            content=content,
            publishedAt=published_at
        )
        logger.info("Article added successfully: %s", title)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse article data: %s", e)
    except AttributeError as e:
        logger.error("Unexpected data format: %s", e)
    except Exception as e:
        logger.error("An error occurred while processing the article: %s", e)


