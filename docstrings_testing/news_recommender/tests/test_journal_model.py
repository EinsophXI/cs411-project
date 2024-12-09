import pytest

from news_recommender.models.journal_model import JournalModel
from news_recommender.models.article_model import Article


@pytest.fixture()
def journal_model():
    """Fixture to provide a new instance of JournalModel for each test."""
    return JournalModel()

@pytest.fixture
def mock_update_read_count(mocker):
    """Mock the update_read_count function for testing purposes."""
    return mocker.patch("news_recommender.models.journal_model.update_read_count")

"""Fixtures providing sample articles for the tests."""
@pytest.fixture
def sample_article1():
    return Article(1, 'Name 1', 'Author 1', 'Title 1', 'URL 1', 'Content 1', '2001-01-01T01:01:01Z')

@pytest.fixture
def sample_article2():
    return Article(2, 'Name 2', 'Author 2', 'Title 2', 'URL 2', 'Content 2', '2002-02-02T02:02:02Z')

@pytest.fixture
def sample_journal(sample_article1, sample_article2):
    return [sample_article1, sample_article2]


##################################################
# Add Article Management Test Cases
##################################################

def test_add_article_to_journal(journal_model, sample_article1):
    """Test adding an article to the journal."""
    journal_model.add_article_to_journal(sample_article1)
    assert len(journal_model.journal) == 1
    assert journal_model.journal[0].title == 'Title 1'

def test_add_duplicate_article_to_journal(journal_model, sample_article1):
    """Test error when adding a duplicate article to the journal by ID."""
    journal_model.add_article_to_journal(sample_article1)
    with pytest.raises(ValueError, match="Article with ID 1 already exists in the journal"):
        journal_model.add_article_to_journal(sample_article1)

##################################################
# Remove Article Management Test Cases
##################################################

def test_remove_article_from_journal_by_article_id(journal_model, sample_journal):
    """Test removing an article from the journal by article_id."""
    journal_model.journal.extend(sample_journal)
    assert len(journal_model.journal) == 2

    journal_model.remove_article_by_article_id(1)
    assert len(journal_model.journal) == 1, f"Expected 1 article, but got {len(journal_model.journal)}"
    assert journal_model.journal[0].id == 2, "Expected article with id 2 to remain"

def test_remove_article_by_article_number(journal_model, sample_journal):
    """Test removing an article from the journal by article number."""
    journal_model.journal.extend(sample_journal)
    assert len(journal_model.journal) == 2

    # Remove article at article number 1 (first article)
    journal_model.remove_article_by_article_number(1)
    assert len(journal_model.journal) == 1, f"Expected 1 article, but got {len(journal_model.journal)}"
    assert journal_model.journal[0].id == 2, "Expected article with id 2 to remain"

def test_clear_journal(journal_model, sample_article1):
    """Test clearing the entire journal."""
    journal_model.add_article_to_journal(sample_article1)

    journal_model.clear_journal()
    assert len(journal_model.journal) == 0, "Journal should be empty after clearing"

def test_clear_journal_empty_journal(journal_model, caplog):
    """Test clearing the entire journal when it's empty."""
    journal_model.clear_journal()
    assert len(journal_model.journal) == 0, "Journal should be empty after clearing"
    assert "Clearing an empty journal" in caplog.text, "Expected warning message when clearing an empty journal"

##################################################
# Articlelisting Management Test Cases
##################################################

def test_move_article_to_article_number(journal_model, sample_journal):
    """Test moving an article to a specific article number in the journal."""
    journal_model.journal.extend(sample_journal)

    journal_model.move_article_to_article_number(2, 1)  # Move Article 2 to the first position
    assert journal_model.journal[0].id == 2, "Expected Article 2 to be in the first position"
    assert journal_model.journal[1].id == 1, "Expected Article 1 to be in the second position"

def test_swap_articles_in_journal(journal_model, sample_journal):
    """Test swapping the positions of two articles in the journal."""
    journal_model.journal.extend(sample_journal)

    journal_model.swap_articles_in_journal(1, 2)  # Swap positions of Article 1 and Article 2
    assert journal_model.journal[0].id == 2, "Expected Article 2 to be in the first position"
    assert journal_model.journal[1].id == 1, "Expected Article 1 to be in the second position"

def test_swap_article_with_itself(journal_model, sample_article1):
    """Test swapping the position of an article with itself raises an error."""
    journal_model.add_article_to_journal(sample_article1)

    with pytest.raises(ValueError, match="Cannot swap an article with itself"):
        journal_model.swap_articles_in_journal(1, 1)  # Swap positions of Article 1 with itself

def test_move_article_to_end(journal_model, sample_journal):
    """Test moving an article to the end of the journal."""
    journal_model.journal.extend(sample_journal)

    journal_model.move_article_to_end(1)  # Move Article 1 to the end
    assert journal_model.journal[1].id == 1, "Expected Article 1 to be at the end"

def test_move_article_to_beginning(journal_model, sample_journal):
    """Test moving an article to the beginning of the journal."""
    journal_model.journal.extend(sample_journal)

    journal_model.move_article_to_beginning(2)  # Move Article 2 to the beginning
    assert journal_model.journal[0].id == 2, "Expected Article 2 to be at the beginning"

##################################################
# Article Retrieval Test Cases
##################################################

def test_get_article_by_article_number(journal_model, sample_journal):
    """Test successfully retrieving an article from the journal by article number."""
    journal_model.journal.extend(sample_journal)

    retrieved_article = journal_model.get_article_by_article_number(1)
    assert retrieved_article.id == 1
    assert retrieved_article.name == 'Name 1'
    assert retrieved_article.author == 'Author 1'
    assert retrieved_article.title == 'Title 1'
    assert retrieved_article.url == 'URL 1'
    assert retrieved_article.content == 'Content 1'
    assert retrieved_article.publishedAt == '2001-01-01T01:01:01Z'

def test_get_all_articles(journal_model, sample_journal):
    """Test successfully retrieving all articles from the journal."""
    journal_model.journal.extend(sample_journal)

    all_articles = journal_model.get_all_articles()
    assert len(all_articles) == 2
    assert all_articles[0].id == 1
    assert all_articles[1].id == 2

def test_get_article_by_article_id(journal_model, sample_article1):
    """Test successfully retrieving an article from the journal by article ID."""
    journal_model.add_article_to_journal(sample_article1)

    retrieved_article = journal_model.get_article_by_article_id(1)

    assert retrieved_article.id == 1
    assert retrieved_article.name == 'Name 1'
    assert retrieved_article.author == 'Author 1'
    assert retrieved_article.title == 'Title 1'
    assert retrieved_article.url == 'URL 1'
    assert retrieved_article.content == 'Content 1'
    assert retrieved_article.publishedAt == '2001-01-01T01:01:01Z'

def test_get_current_article(journal_model, sample_journal):
    """Test successfully retrieving the current article from the journal."""
    journal_model.journal.extend(sample_journal)

    current_article = journal_model.get_current_article()
    assert current_article.id == 1
    assert current_article.name == 'Name 1'
    assert current_article.author == 'Author 1'
    assert current_article.title == 'Title 1'
    assert current_article.url == 'URL 1'
    assert current_article.content == 'Content 1'
    assert current_article.publishedAt == '2001-01-01T01:01:01Z'

def test_get_journal_length(journal_model, sample_journal):
    """Test getting the length of the journal."""
    journal_model.journal.extend(sample_journal)
    assert journal_model.get_journal_length() == 2, "Expected journal length to be 2"

##################################################
# Utility Function Test Cases
##################################################

def test_check_if_empty_non_empty_journal(journal_model, sample_article1):
    """Test check_if_empty does not raise error if journal is not empty."""
    journal_model.add_article_to_journal(sample_article1)
    try:
        journal_model.check_if_empty()
    except ValueError:
        pytest.fail("check_if_empty raised ValueError unexpectedly on non-empty journal")

def test_check_if_empty_empty_journal(journal_model):
    """Test check_if_empty raises error when journal is empty."""
    journal_model.clear_journal()
    with pytest.raises(ValueError, match="Journal is empty"):
        journal_model.check_if_empty()

def test_validate_article_id(journal_model, sample_article1):
    """Test validate_article_id does not raise error for valid article ID."""
    journal_model.add_article_to_journal(sample_article1)
    try:
        journal_model.validate_article_id(1)
    except ValueError:
        pytest.fail("validate_article_id raised ValueError unexpectedly for valid article ID")

def test_validate_article_id_no_check_in_journal(journal_model):
    """Test validate_article_id does not raise error for valid article ID when the id isn't in the journal."""
    try:
        journal_model.validate_article_id(1, check_in_journal=False)
    except ValueError:
        pytest.fail("validate_article_id raised ValueError unexpectedly for valid article ID")

def test_validate_article_id_invalid_id(journal_model):
    """Test validate_article_id raises error for invalid article ID."""
    with pytest.raises(ValueError, match="Invalid article id: -1"):
        journal_model.validate_article_id(-1)

    with pytest.raises(ValueError, match="Invalid article id: invalid"):
        journal_model.validate_article_id("invalid")

def test_validate_article_number(journal_model, sample_article1):
    """Test validate_article_number does not raise error for valid article number."""
    journal_model.add_article_to_journal(sample_article1)
    try:
        journal_model.validate_article_number(1)
    except ValueError:
        pytest.fail("validate_article_number raised ValueError unexpectedly for valid article number")

def test_validate_article_number_invalid(journal_model, sample_article1):
    """Test validate_article_number raises error for invalid article number."""
    journal_model.add_article_to_journal(sample_article1)

    with pytest.raises(ValueError, match="Invalid article number: 0"):
        journal_model.validate_article_number(0)

    with pytest.raises(ValueError, match="Invalid article number: 2"):
        journal_model.validate_article_number(2)

    with pytest.raises(ValueError, match="Invalid article number: invalid"):
        journal_model.validate_article_number("invalid")

##################################################
# Readback Test Cases
##################################################

def test_read_current_article(journal_model, sample_journal, mock_update_read_count):
    """Test reading the current article."""
    journal_model.journal.extend(sample_journal)

    journal_model.read_current_article()

    # Assert that CURRENT_ARTICLE_NUMBER has been updated to 2
    assert journal_model.current_article_number == 2, f"Expected article number to be 2, but got {journal_model.current_article_number}"

    # Assert that update_read_count was called with the id of the first article
    mock_update_read_count.assert_called_once_with(1)

    # Get the second article from the iterator (which will increment CURRENT_ARTICLE_NUMBER back to 1)
    journal_model.read_current_article()

    # Assert that CURRENT_ARTICLE_NUMBER has been updated back to 1
    assert journal_model.current_article_number == 1, f"Expected article number to be 1, but got {journal_model.current_article_number}"

    # Assert that update_read_count was called with the id of the second article
    mock_update_read_count.assert_called_with(2)

def test_rewind_journal(journal_model, sample_journal):
    """Test rewinding the iterator to the beginning of the journal."""
    journal_model.journal.extend(sample_journal)
    journal_model.current_article_number = 2

    journal_model.rewind_journal()
    assert journal_model.current_article_number == 1, "Expected to rewind to the first article"

def test_go_to_article_number(journal_model, sample_journal):
    """Test moving the iterator to a specific article number in the journal."""
    journal_model.journal.extend(sample_journal)

    journal_model.go_to_article_number(2)
    assert journal_model.current_article_number == 2, "Expected to be at article 2 after moving article"

def test_read_entire_journal(journal_model, sample_journal, mock_update_read_count):
    """Test reading the entire journal."""
    journal_model.journal.extend(sample_journal)

    journal_model.read_entire_journal()

    # Check that all read counts were updated
    mock_update_read_count.assert_any_call(1)
    mock_update_read_count.assert_any_call(2)
    assert mock_update_read_count.call_count == len(journal_model.journal)

    # Check that the current article number was updated back to the first article
    assert journal_model.current_article_number == 1, "Expected to loop back to the beginning of the journal"

def test_read_rest_of_journal(journal_model, sample_journal, mock_update_read_count):
    """Test reading from the current position to the end of the journal."""
    journal_model.journal.extend(sample_journal)
    journal_model.current_article_number = 2

    journal_model.read_rest_of_journal()

    # Check that read counts were updated for the remaining articles
    mock_update_read_count.assert_any_call(2)
    assert mock_update_read_count.call_count == 1

    assert journal_model.current_article_number == 1, "Expected to loop back to the beginning of the journal"