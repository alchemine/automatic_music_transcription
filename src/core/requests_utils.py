"""Requests module for handling HTTP requests."""

from typing import Any

import requests
from requests import Response, RequestException
import asyncio
import aiohttp

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


async def post_request(session: aiohttp.ClientSession, url: str, data: dict) -> list | dict:
    """Post request using aiohttp.

    Args:
        session (aiohttp.ClientSession): aiohttp session.
        url (str): URL to post.
        data (dict): Data to post.

    Returns:
        list | dict: Response data.
    """
    async with session.post(
        url=url,
        headers=HEADERS,
        json=data,
    ) as response:
        response.raise_for_status()
        return await response.json()


async def async_post(url: str, batch: list[dict]) -> list[Any]:
    """Post requests asynchronously.

    Args:
        url (str): URL to post.
        batch (list[dict]): List of data to post.

    Returns:
        list[Any]: List of response data.
    
    Examples:
        import asyncio
        asyncio.run(async_post(url, batch))
    """
    async with aiohttp.ClientSession() as session:
        futures = [post_request(session, url, data) for data in batch]
        responses = await asyncio.gather(*futures)
    return responses


if __name__ == "__main__":
    url = "https://httpbin.org/post"
    json = {"key": "value"}
    response = safe_post(url, json)
