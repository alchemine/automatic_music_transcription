"""Requests module for handling HTTP requests."""

import requests
from requests import Response, RequestException

from src.core.logger import log_api


HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
}


class APIError(Exception):
    """API Error exception.

    Args:
        url (str): The URL of the API.
        headers (dict): The headers of the API.
        json (dict): The JSON data of the API.
        response (Response): The response of the API.

    Returns:
        str: The API error message.
    """

    def __init__(self, url: str, headers: dict, json: dict, response: Response):
        self.url = url
        self.headers = headers
        self.json = json
        self.response = response

    def __str__(self):
        return f"""APIError: <Response [{self.response.status_code}]>
requests.post(
    url="{self.url}",
    headers={self.headers},
    json={self.json}
) -> {self.response.json()}"""


def get_request_log(
    url: str, headers: dict, json: dict, response: Response | None = None
) -> dict:
    """Get the request log.

    Args:
        url (str): The URL of the API.
        headers (dict): The headers of the API.
        json (dict): The JSON data of the API.
        response (Response): The response of the API.

    Returns:
        dict: The request log.
    """
    log = dict(
        url=url,
        headers=headers,
        json=json,
        reproduction_code=f"import requests; requests.post(url='{url}', headers={headers}, json={json})",
    )

    if response:
        log.update(
            response=dict(status_code=response.status_code, json=response.json())
        )

    return log


def safe_post(url: str, json: dict, headers: dict = HEADERS) -> dict:
    """Requests post with validation.

    Args:
        url (str): The URL of the API.
        json (dict): The JSON data of the API.
        headers (dict): The headers of the API.

    Returns:
        Response: The response of the API.
    """
    # Check the API communication validness
    try:
        response = requests.post(url=url, headers=headers, json=json)
        response.raise_for_status()
        log = get_request_log(url, headers, json)
        log_api(log)
        return response.json()
    except RequestException as e:
        log = get_request_log(url, headers, json)
        log_api(log, error=True)
        raise APIError(url, headers, json, response)


if __name__ == "__main__":
    url = "https://httpbin.org/post"
    json = {"key": "value"}
    response = safe_post(url, json)
