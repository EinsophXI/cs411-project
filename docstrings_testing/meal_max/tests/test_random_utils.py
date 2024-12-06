import pytest
import requests
from meal_max.utils.random_utils import get_random


RANDOM_NUMBER = 15  # Expected random value for testing purposes


@pytest.fixture
def mock_random_service(mocker):
    # Create a mock object for the response from the requests.get call
    mock_response = mocker.Mock()
    mock_response.text = f"{RANDOM_NUMBER}" 
    mocker.patch("requests.get", return_value=mock_response)  
    return mock_response


def test_get_random_number(mock_random_service):
    """Verify retrieval of the expected random number from random.org using get_random."""
    result = get_random()  # Call the function to get a random number
    # Makes sure the result matches the expected random number
    assert result == RANDOM_NUMBER, f"Expected {RANDOM_NUMBER} as the random number, received {result}"  
    # Confirms that the correct URL was requested and with the expected timeout
    requests.get.assert_called_once_with(
        "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new",
        timeout=5)  


def test_get_random_number_request_failure(mocker):
    """Simulate request failure when accessing random.org."""
    # Mock a request failure by raising a RequestException
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error")) 
    # Makes sure that a RuntimeError is raised with the correct message
    with pytest.raises(RuntimeError, match=r"Request to random\.org failed: Connection error"):
        get_random()


def test_get_random_number_timeout(mocker):
    """Simulate a timeout error for requests to random.org."""
    # Mock a timeout error for the requests.get call
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)  
    # Makes sure that a RuntimeError is raised with the correct timeout message
    with pytest.raises(RuntimeError, match=r"Request to random\.org timed out\."):
        get_random()


def test_get_random_number_invalid_response(mock_random_service):
    """Handle non-numeric response from random.org."""
    # Set the mock response to return a non-numeric value
    mock_random_service.text = "invalid_response" 
    # Makes sure that a ValueError is raised with the correct error message for invalid response
    with pytest.raises(ValueError, match=r"Invalid response from random\.org: invalid_response"):
        get_random()