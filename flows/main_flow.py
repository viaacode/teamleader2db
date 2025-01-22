import json
from functools import partial

from prefect import flow, get_run_logger

from models import *
from database import *
from teamleader import *


def prepare_info_list(infos: list[TL_ResponseInfo]) -> list[tuple]:
    """
    Prepare the Teamleader responses for upload to the database.
    """
    return [
        (str(info.data["id"]), "companies", json.dumps(info.data)) for info in infos
    ]


@flow(name="Teamleader2db resource sync")
def sync_teamleader_resource(
    tl_uri: str,
    resource: Resource,
    full_sync: bool,
    conn: Connection,
    auth: TL_Auth,
) -> TL_Auth:
    """
    Sync a Teamleader resource (companies, users, contacts, etc.) to the etl_harvest database.

    TL_Auth is returned from this flow because `refresh_auth_token` might have been during the execution of this flow.
    """

    logger = get_run_logger()
    resource_table_name = Resource.get_db_table_name(resource)
    logger.info(f"Starting sync of {resource} to {resource_table_name}")

    create_teamleader_resource_table(resource, conn)

    if full_sync:
        truncate_table(conn, resource_table_name)
        db_last_modified = None
    else:
        db_last_modified = get_last_modified_date(conn, resource_table_name)

    RequestList = partial(
        TL_RequestList,
        base_uri=tl_uri,
        resource=resource,
        updated_since=db_last_modified,
    )

    RequestInfo = partial(
        TL_RequestInfo,
        base_uri=tl_uri,
        resource=resource,
    )

    page = 1
    total = 0
    while True:
        req = RequestList(page=page)

        response_list = request_teamleader_list(req, auth, conn)
        auth = response_list.auth
        page += 1
        total += len(response_list.data)

        if len(response_list.data) == 0:
            break

        details = []
        for item in response_list.data:
            req = RequestInfo(id=item["id"])
            info = request_teamleader_info(req, auth, conn)
            details.append(info)

        rows = prepare_info_list(details)
        upsert_into_table(conn, resource_table_name, rows)
        logger.info(f"Synced {total} {resource.name} items to {resource_table_name}")

    return auth


@flow(name="Teamleader2db")
def main_flow(
    tl_client: TL_Client,
    tl_api_uri: str = "https://api.focus.teamleader.eu",
    tl_auth_uri: str = "https://focus.teamleader.eu/oauth2",
    db_block_name: str = "etl-harvest",
    full_sync: bool = False,
    test_db_conn: Optional[Connection] = None,
):

    conn = connect_database(db_block_name) if test_db_conn is None else test_db_conn
    create_teamleader_auth_table(conn)
    auth = get_auth_tokens_from_db(conn, tl_auth_uri, tl_client)

    for resource in Resource:
        auth = sync_teamleader_resource(tl_api_uri, resource, full_sync, conn, auth)


if __name__ == "__main__":
    from os import environ

    main_flow(
        tl_client=TL_Client(
            client_id=environ["TL_CLIENT_ID"],
            client_secret=SecretStr(environ["TL_CLIENT_SECRET"]),
        ),
        full_sync=True,
    )
