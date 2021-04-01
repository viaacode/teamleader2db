#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from psycopg2 import OperationalError as PSQLError

from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.comm.teamleader_client import TeamleaderClient
from app.comm.companies import Companies
from app.comm.contacts import Contacts


# TODO: these tables:
# status['departments'] = state.app.contacts_status()
# status['events'] = state.app.contacts_status()
# status['invoices'] = state.app.contacts_status()
# status['projects'] = state.app.contacts_status()
# status['users'] = state.app.contacts_status()


import argh

# Initialize the logger and the configuration
config = ConfigParser()
logger = logging.get_logger(__name__, config=config)


class App:

    def __init__(self):
        # Initialize teamleader and target database tables
        self.tl_client = TeamleaderClient(config.app_cfg['teamleader'])

        self.companies = Companies(
            config.app_cfg['postgresql_teamleader'],
            config.app_cfg['table_names']
        )
        self.contacts = Contacts(
            config.app_cfg['postgresql_teamleader'],
            config.app_cfg['table_names']
        )

    def auth_callback(self, code, state):
        return self.tl_client.auth_code_callback(code, state)

    def companies_sync(self, modified_since: datetime = None):
        """ Syncs teamleader companies into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader entries.
        """

        # if not modified_since:
        #     modified_since = self.companies.max_last_modified_timestamp()

        logger.info("companies sync started...")
        page = 1
        resp = [1]
        total_synced = 0
        while len(resp) > 0:
            resp = self.tl_client.list_companies(page, 100, modified_since)
            page += 1
            total_synced += len(resp)
            print(f"TODO: save {len(resp)} companies in db.", flush=True)

        logger.info(f"Done, synchronized {total_synced} companies")

    def contacts_sync(self, modified_since: datetime = None):
        """ Syncs teamleader contacts into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader entries.
        """
        # if not modified_since:
        #     modified_since = self.contacts.max_last_modified_timestamp()

        logger.info("contacts sync...")
        page = 1
        resp = [1]
        total_synced = 0
        while len(resp) > 0:
            resp = self.tl_client.list_contacts(page, 100, modified_since)
            page += 1
            print(f"TODO: save {len(resp)} contacts in db.", flush=True)
            total_synced += len(resp)

        logger.info(f"Done, synchronized {total_synced} contacts")

    def companies_status(self):
        return self.companies.status()

    def contacts_status(self):
        return self.contacts.status()

    def teamleader_sync(self, full_sync=False):
        if full_sync:
            logger.info("Start full sync from teamleader")
            self.companies.truncate_table()
            self.contacts.truncate_table()
            # self.departments.truncate_table()
            # self.invoices.truncate_table()
            # self.projects.truncate_table()
            # self.users.truncate_table()
        else:
            logger.info("Start delta sync from teamleader")

        self.companies_sync()
        self.contacts_sync()

        logger.info("Teamleader sync completed")

    def main(self):
        try:
            argh.dispatch_commands([
                self.companies_status,
                self.contacts_status,
                self.companies_sync,
                self.contacts_sync,
                self.teamleader_sync
            ])
        except (PSQLError) as e:
            logger.error(e)
            raise e


if __name__ == "__main__":
    App().main()
