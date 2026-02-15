from typing import Dict, Any, Optional
import httpx
from langchain.tools import tool
import asyncio

class APIExecutionResult(dict):
    """
    Normalized API response returned to LangGraph / LLM
    """
    pass

@tool
async def execute_api(
    *,
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    query_params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    timeout: float = 10.0,
) -> APIExecutionResult:
    ''''
    Execute an HTTP request asynchronously and return a standardized result.

    This function performs an HTTP request using the specified method and URL.
    Optional headers, query parameters, and JSON body payload may be provided.

    If the response contains valid JSON, it is returned in the ``body`` field.
    Otherwise, the raw response text is returned. Timeout and request-level
    errors are caught and returned as structured error responses.

    :param method: HTTP method to use (e.g., "GET", "POST", "PUT", "DELETE").
                   The value is normalized to uppercase.
    :type method: str
    :param url: The full URL of the endpoint to call.
    :type url: str
    :param headers: Optional dictionary of HTTP headers to include in the request.
    :type headers: Optional[Dict[str, str]]
    :param query_params: Optional dictionary of query string parameters to append
                         to the URL.
    :type query_params: Optional[Dict[str, Any]]
    :param json_body: Optional dictionary to send as a JSON request body.
                      Ignored for methods that do not support bodies.
    :type json_body: Optional[Dict[str, Any]]
    :param timeout: Request timeout in seconds. Defaults to 10.0 seconds.
    :type timeout: float
    :return: A dictionary containing:
             - ``ok`` (bool): Whether the request was successful (2xx status).
             - ``status_code`` (int): HTTP response status code (if available).
             - ``headers`` (Dict[str, str]): Response headers (if available).
             - ``body`` (Any): Parsed JSON response or raw text.
             - ``error`` (str, optional): Error message if the request failed.
    :rtype: APIExecutionResult
    :raises: Does not raise exceptions. All handled errors are returned
             as structured responses.
    '''
    method = method.upper()
    print("------------------------------------------------------------\n")
    print(f"Executing API call: {method} {url}")
    print("--------------------------------------------------------------\n")
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=query_params,
                json=json_body,
            )

        result: APIExecutionResult = {
            "ok": response.is_success,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": _safe_json(response),
        }

        print("\n------------------- API RESPONSE -------------------")
        print("Response:", result)
        print("----------------------------------------------------\n")

        return result

    except httpx.TimeoutException:
        return {
            "ok": False,
            "error": "Request timed out",
        }

    except httpx.RequestError as e:
        return {
            "ok": False,
            "error": str(e),
        }


def _safe_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except Exception:
        return response.text




# async def test():
#     result = await execute_api(
#         method="GET",
#         url="https://jsonplaceholder.typicode.com/posts/1",
#     )
#     print(result)

# asyncio.run(test())
