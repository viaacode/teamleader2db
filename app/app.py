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
        self.tlc = TeamleaderClient(config.app_cfg['teamleader'])

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
        return self.tlc.auth_code_callback(code, state)

    def resource_sync(self, name, tl_method, model, modified_since=None):
        # TODO: fix ts format now its 2021-04-01 16:30:07.884493+02:00
        # but see teamleader client, it should be other format...
        # if not modified_since:
        #     modified_since = model.max_last_modified_timestamp()

        logger.info(f"{name} sync since {modified_since} started...")
        page = 1
        resp = [1]
        total_synced = 0
        while len(resp) > 0:
            resp = tl_method(page, 100, modified_since)
            if len(resp) > 0:
                model.upsert_results([(resp, name)])
                page += 1
                total_synced += len(resp)
                print(f"{name} synced = {len(resp)}", flush=True)

        logger.info(f"Done, synchronized {total_synced} {name}")

    def companies_sync(self, modified_since: datetime = None):
        """ Syncs teamleader companies into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader entries.
        """
        self.resource_sync(
            'companies', self.tlc.list_companies, self.companies, modified_since)

    def contacts_sync(self, modified_since: datetime = None):
        """ Syncs teamleader contacts into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader entries.
        """
        self.resource_sync(
            'contacts', self.tlc.list_contacts, self.contacts, modified_since)

    def departments_sync(self, modified_since: datetime = None):
        """ Syncs teamleader departments into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader entries.
        """
        self.resource_sync(
            'departments', self.tlc.list_departments, self.departments, modified_since)

    def events_sync(self, modified_since: datetime = None):
        """ Syncs teamleader events into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader entries.
        """
        self.resource_sync('events', self.tlc.list_events,
                           self.events, modified_since)

    def invoices_sync(self, modified_since: datetime = None):
        """ Syncs teamleader invoices into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader invoices.
        """
        self.resource_sync(
            'invoices', self.tlc.list_invoices, self.invoices, modified_since)

    def projects_sync(self, modified_since: datetime = None):
        """ Syncs teamleader projects into target database

            Arguments:
            modified_since -- Filters teamleader projects with updated_since
                              If None, it will retrieve all teamleader projects.
        """
        self.resource_sync(
            'projects', self.tlc.list_projects, self.projects, modified_since)

    def users_sync(self, modified_since: datetime = None):
        """ Syncs teamleader users into target database

            Arguments:
            modified_since -- Filters teamleader users with updated_since
                              If None, it will retrieve all teamleader users.
        """
        self.resource_sync('users', self.tlc.list_users,
                           self.users, modified_since)

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
        self.invoices_sync()
        self.projects_sync()
        self.users_sync()

        logger.info("Teamleader sync completed")

    def teamleader_status(self):
        status = {}
        status['companies'] = self.companies.status()
        status['contacts'] = self.contacts.status()
        status['departments'] = self.departments.status()
        status['events'] = self.events.status()
        status['invoices'] = self.invoices.status()
        status['projects'] = self.projects.status()
        status['users'] = self.users.status()

        return status

    def main(self):
        try:
            argh.dispatch_commands([
                self.companies_sync,
                self.departments_sync,
                self.events_sync,
                self.invoices_sync,
                self.projects_sync,
                self.users_sync,
                self.teamleader_sync,
                self.teamleader_status
            ])
        except (PSQLError) as e:
            logger.error(e)
            raise e


if __name__ == "__main__":
    App().main()
