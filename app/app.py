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
#status['departments'] = state.app.contacts_status()
#status['events'] = state.app.contacts_status()
#status['invoices'] = state.app.contacts_status()
#status['projects'] = state.app.contacts_status()
#status['users'] = state.app.contacts_status()


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

    def companies_sync(self, modified_since: datetime = None):
        """ Syncs teamleader clients into target database 

            Arguments:
            modified_since -- Searches the LDAP results based on this parameter.
                              If None, it will retrieve all LDAP entries.
        """

        if not modified_since:
            modified_since = self.companies.max_last_modified_timestamp()

        logger.info("companies sync")

        return 'TODO'

    def contacts_sync(self, modified_since: datetime = None):
        """ Syncs teamleader organizations into target database 

            Arguments:
            modified_since -- Searches the LDAP results based on this parameter.
                              If None, it will retrieve all LDAP entries.
        """
        if not modified_since:
            modified_since = self.contacts.max_last_modified_timestamp()

        logger.info("contacts sync")
        # watch out for rate limit of 100 calls per minute !
        return 'TODO'

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
