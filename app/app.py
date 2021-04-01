#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from psycopg2 import OperationalError as PSQLError

from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.comm.teamleader_client import TeamleaderClient
from app.comm.companies import Companies
from app.comm.contacts import Contacts
from app.comm.departments import Departments
from app.comm.events import Events
from app.comm.invoices import Invoices
from app.comm.projects import Projects
from app.comm.users import Users


import argh

# Initialize the logger and the configuration
config = ConfigParser()
logger = logging.get_logger(__name__, config=config)


class App:

    def __init__(self):
        # Initialize teamleader and target database tables
        self.tl_client = TeamleaderClient(config.app_cfg['teamleader'])

        db_conf = config.app_cfg['postgresql_teamleader']
        table_names = config.app_cfg['table_names']
        self.companies = Companies(db_conf, table_names)
        self.contacts = Contacts(db_conf, table_names)
        self.departments = Departments(db_conf, table_names)
        self.events = Events(db_conf, table_names)
        self.invoices = Invoices(db_conf, table_names)
        self.projects = Projects(db_conf, table_names)
        self.users = Users(db_conf, table_names)

    def auth_callback(self, code, state):
        return self.tl_client.auth_code_callback(code, state)

    def companies_sync(self, modified_since: datetime = None):
        """ Syncs teamleader companies into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader entries.
        """

        # fix ts format now its 2021-04-01 16:30:07.884493+02:00
        # but see teamleader client, it should be other format...
        # if not modified_since:
        #     modified_since = self.companies.max_last_modified_timestamp()

        logger.info(f"Companies sync since {modified_since} started...")
        page = 1
        resp = [1]
        total_synced = 0
        while len(resp) > 0:
            resp = self.tl_client.list_companies(page, 100, modified_since)
            if len(resp) > 0:
                self.companies.upsert_results([(resp, "companies")])
                page += 1
                total_synced += len(resp)
                print(f"companies synced = {total_synced}", flush=True)

        logger.info(f"Done, synchronized {total_synced} companies")

    def contacts_sync(self, modified_since: datetime = None):
        """ Syncs teamleader contacts into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader entries.
        """
        # if not modified_since:
        #     modified_since = self.contacts.max_last_modified_timestamp()

        logger.info(f"Contacts sync since {modified_since} started...")
        page = 1
        resp = [1]
        total_synced = 0
        while len(resp) > 0:
            resp = self.tl_client.list_contacts(page, 100, modified_since)
            if len(resp) > 0:
                self.contacts.upsert_results([(resp, "contacts")])
                page += 1
                total_synced += len(resp)
                print(f"contacts synced = {total_synced}", flush=True)

        logger.info(f"Done, synchronized {total_synced} contacts")

    def departments_sync(self, modified_since: datetime = None):
        """ Syncs teamleader departments into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader entries.
        """
        # if not modified_since:
        #     modified_since = self.contacts.max_last_modified_timestamp()

        logger.info(f"departments sync since {modified_since} started...")
        page = 1
        resp = [1]
        total_synced = 0
        while len(resp) > 0:
            resp = self.tl_client.list_departments(page, 100, modified_since)
            if len(resp) > 0:
                self.departments.upsert_results([(resp, "departments")])
                page += 1
                total_synced += len(resp)
                print(f"departments synced = {total_synced}", flush=True)

        logger.info(f"Done, synchronized {total_synced} departments")

    def events_sync(self, modified_since: datetime = None):
        """ Syncs teamleader events into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader entries.
        """
        # if not modified_since:
        #     modified_since = self.contacts.max_last_modified_timestamp()

        logger.info(f"events sync since {modified_since} started...")
        page = 1
        resp = [1]
        total_synced = 0
        while len(resp) > 0:
            resp = self.tl_client.list_events(page, 100, modified_since)
            if len(resp) > 0:
                self.events.upsert_results([(resp, "events")])
                page += 1
                total_synced += len(resp)
                print(f"events synced = {total_synced}", flush=True)

        logger.info(f"Done, synchronized {total_synced} events")

    def companies_status(self):
        return self.companies.status()

    def contacts_status(self):
        return self.contacts.status()

    def teamleader_sync(self, full_sync=False):
        if full_sync:
            logger.info("Start full sync from teamleader")
            self.companies.truncate_table()
            self.contacts.truncate_table()
            self.departments.truncate_table()
            self.events.truncate_table()
            self.invoices.truncate_table()
            self.projects.truncate_table()
            self.users.truncate_table()
        else:
            logger.info("Start delta sync from teamleader")

        self.companies_sync()
        self.contacts_sync()
        self.departments_sync()
        self.events_sync()
        # self.invoices_sync()
        # self.projects_sync()
        # self.users_sync()

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
