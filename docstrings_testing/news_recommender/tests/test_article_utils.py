import pytest
import requests

from news_recommender.utils.article_utils import get_articles


ARTICLE_KEYWORD = "keyword"
NUM_ARTS = 1

@pytest.fixture
def mock_newsapi_org(mocker):
    # Patch the requests.get call
    # requests.get returns an object, which we have replaced with a mock object
    mock_response = mocker.Mock()
    # We are giving that object a text attribute
    mock_response.text = f"{ARTICLE_KEYWORD}"
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response


def test_get_articles(mock_newsapi_org):
    """Test retrieving an article from newsapi.org"""
    result = get_articles(ARTICLE_KEYWORD, NUM_ARTS)

    parsed_response = requests.get().text  # Simulating the returned mock text
    result = parsed_response.get("status")
    # Assert that the result is the mocked result
    assert result == "ok", f"Error: Got {result}, "

    # Ensure that the correct URL was called
    requests.get.assert_called_once_with("https://newsapi.org/v2/everything?q=%7Bkeyword%7D&pagesize=1&apiKey=e616acff8a674cfc8ba4648026e85f1d", timeout=5)

def test_get_articles_request_failure(mocker):
    """Simulate  a request failure."""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"))

    with pytest.raises(RuntimeError, match="Request to newsapi.org failed: Connection error"):
        get_articles(ARTICLE_KEYWORD, NUM_ARTS)

def test_get_articles_timeout(mocker):
    """Simulate  a timeout."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to newsapi.org timed out."):
        get_articles(ARTICLE_KEYWORD, NUM_ARTS)

def test_get_articles_invalid_response(mock_newsapi_org):
    """Simulate  an invalid response"""
    mock_newsapi_org.text = "invalid_response"

    with pytest.raises(ValueError, match="Invalid response from newsapi.org: invalid_response"):
        get_articles(ARTICLE_KEYWORD, NUM_ARTS)
