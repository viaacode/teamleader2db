from time import sleep
from typing import Any, Union, cast
from datetime import datetime

from prefect import task, get_run_logger
import requests
from requests import Response

from models import *
from database import *


class TeamleaderRequestException(Exception):
    pass


@task
def refresh_auth_token(conn: Connection, auth: TL_Auth) -> TL_Auth:
    logger = get_run_logger()
    logger.info("Refreshing access token")

    # Check if the database is in a valid state
    validate_db_auth_state(conn)

    # Refresh the authorization token
    response = requests.post(
        auth.uri + "/access_token",
        data={
            "client_id": auth.client_id,
            "client_secret": auth.client_secret.get_secret_value(),
            "refresh_token": auth.refresh_token.get_secret_value(),
            "grant_type": "refresh_token",
        },
    )
    if response.status_code != 200:
        raise Exception(
            f"Could not refresh token. Status code {response.status_code} - {response.reason}"
        )
    response = response.json()

    auth = TL_Auth(
        uri=auth.uri,
        client_id=auth.client_id,
        client_secret=auth.client_secret,
        refresh_token=response["refresh_token"],  # Does this need a SecretStr() ?
        access_token=response["access_token"],  # idem
    )

    save_tokens_to_database(auth, conn)
    logger.info("Updated access token and refresh token in database.")
    return auth


def get_request_headers(auth: TL_Auth):
    return {"Authorization": f"Bearer {auth.access_token.get_secret_value()}"}


def request_teamleader_info(
    req: TL_RequestInfo,
    auth: TL_Auth,
    conn: Connection,
) -> TL_ResponseInfo:
    response = request_teamleader(req, auth, conn)
    return TL_ResponseInfo(
        resource=response.resource,
        ratelimit_remaining=response.ratelimit_remaining,
        ratelimit_reset=response.ratelimit_reset,
        data=cast(dict[str, Any], response.data),
        auth=response.auth,
    )


def request_teamleader_list(
    req: TL_RequestList,
    auth: TL_Auth,
    conn: Connection,
) -> TL_ResponseList:
    response = request_teamleader(req, auth, conn)
    return TL_ResponseList(
        resource=response.resource,
        ratelimit_remaining=response.ratelimit_remaining,
        ratelimit_reset=response.ratelimit_reset,
        data=cast(list[dict[str, Any]], response.data),
        auth=response.auth,
    )


@task(retries=5, retry_delay_seconds=1)
def requests_post(url: str, data: dict[str, Any], headers: dict[str, str]) -> Response:
    return requests.post(url, headers=headers, data=data)


def request_teamleader(
    req: Union[TL_RequestList, TL_RequestInfo],
    auth: TL_Auth,
    conn: Connection,
) -> TL_Response:
    logger = get_run_logger()
    logger.info(f"POST request - {req}")

    data = serialize(req)
    headers = get_request_headers(auth)
    response = requests_post(req.path, headers=headers, data=data)

    if response.status_code == 401:  # Unauthorized
        logger.info(f"{response.status_code} - {response.reason}")
        auth = refresh_auth_token(conn, auth)
        headers = get_request_headers(auth)
        sleep(3)
        response = requests_post(req.path, headers=headers, data=data)

    if response.status_code != 200:
        raise TeamleaderRequestException(
            f"Could not complete teamleader request. Status code {response.status_code} - {response.reason} - {response.text}"
        )

    response = TL_Response(
        resource=req.resource,
        ratelimit_remaining=int(response.headers["X-RateLimit-Remaining"]),
        ratelimit_reset=datetime.fromisoformat(response.headers["X-RateLimit-Reset"]),
        data=response.json()["data"],
        auth=auth,
    )

    if response.ratelimit_remaining < 5:
        logger.info("Requests rate limit low. Sleeping for 60 seconds...")
        sleep(60)

    return response
