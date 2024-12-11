import pytest
import requests

from news_recommender.utils.article_utils import get_articles


ARTICLE_KEYWORD = "keyword"
NUM_ARTS = 1

@pytest.fixture
def mock_newsapi_org(mocker):
    # Create a mock response object
    mock_response = mocker.Mock()
    
    # Set up .json() to return mock JSON data
    mock_response.json.return_value = {
        "status": "ok",
        "totalResults": 852,
        "articles": [
            {
            "source": {
                "id": "the-verge",
                "name": "The Verge"
            },
            "author": "Wes Davis",
            "title": "Threads’ next update is a search feature that finds the post you’re looking for",
            "description": "Threads is rolling out the ability to search for posts from a specific profile and inside your chosen date ranges.",
            "url": "https://www.theverge.com/2024/12/2/24311435/threads-search-tool-before-after-date-profile-filters",
            "urlToImage": "https://cdn.vox-cdn.com/thumbor/7F_fPNt4RPcVyi-RPF6ww3eAHOg=/11x40:1335x688/1200x628/filters:focal(679x321:680x322)/cdn.vox-cdn.com/uploads/chorus_asset/file/25770219/Threads_search_update.png",
            "publishedAt": "2024-12-02T22:08:33Z",
            "content": "Threads next update is a search feature that finds the post youre looking for\r\nThreads next update is a search feature that finds the post youre looking for\r\n / Youll be able to search for posts filt… [+1555 chars]"
            }
        ]
    }

    # Patch the requests.get call to return this mock response
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response


def test_get_articles(mock_newsapi_org):
    """Test retrieving an article from newsapi.org."""
    result = get_articles(ARTICLE_KEYWORD, NUM_ARTS)

    # Assert that the result matches the mock article
    assert result["title"] == "Threads’ next update is a search feature that finds the post you’re looking for", f"Expected 'Threads’ next update is a search feature that finds the post you’re looking for', got {result.get('title')}"
    assert result["author"] == "Wes Davis", f"Expected 'Wes Davis', got {result.get('author')}"

    # Ensure that the correct URL was called
    requests.get.assert_called_once_with(
        f"https://newsapi.org/v2/everything?q={ARTICLE_KEYWORD}&pageSize={NUM_ARTS}&apiKey=e616acff8a674cfc8ba4648026e85f1d",
        timeout=5
    )

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

def test_get_articles_invalid_response(mocker):
    """Simulate an invalid response."""
    mock_response = mocker.Mock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mocker.patch("requests.get", return_value=mock_response)

    with pytest.raises(RuntimeError, match="Invalid response received: Invalid JSON"):
        get_articles(ARTICLE_KEYWORD, NUM_ARTS)
