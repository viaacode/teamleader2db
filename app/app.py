#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#   app/app.py
#
#   Main application this exposes some methods for syncing and csv exports
#   using the argh library
#
#   The same methods are also linked to a swagger ui / fastapi json api calls.
#   See api folder for the routers and routes in api.py and server.py where
#   this is instantiated
#
import argh
from psycopg2 import OperationalError as PSQLError
from viaa.configuration import ConfigParser
from viaa.observability import logging
from app.comm.teamleader_client import TeamleaderClient
from app.models.companies import Companies
from app.models.contacts import Contacts
from app.models.departments import Departments
from app.models.events import Events
from app.models.invoices import Invoices
from app.models.projects import Projects
from app.models.users import Users
from app.models.custom_fields import CustomFields


# Initialize the logger and the configuration
config = ConfigParser()
logger = logging.get_logger(__name__, config=config)


class App:

    def __init__(self):
        self.init_teamleader_client()
        self.init_database_models()

    def init_teamleader_client(self):
        self.tlc = TeamleaderClient(config.app_cfg)

    def init_database_models(self):
        db_conf = config.app_cfg['postgresql_teamleader']
        table_names = config.app_cfg['table_names']

        self.companies = Companies(db_conf, table_names)
        self.contacts = Contacts(db_conf, table_names)
        self.departments = Departments(db_conf, table_names)
        self.events = Events(db_conf, table_names)
        self.invoices = Invoices(db_conf, table_names)
        self.projects = Projects(db_conf, table_names)
        self.users = Users(db_conf, table_names)
        self.custom_fields = CustomFields(db_conf, table_names)

    def auth_callback(self, code, state):
        return self.tlc.authcode_callback(code, state)

    def resource_sync(self, list_call, details_call, model, full_sync=False):
        if full_sync:
            model.truncate_table()

        modified_since = model.max_last_modified_timestamp()
        if modified_since:
            logger.info(
                f"{model.name} delta since {modified_since.isoformat()} started.")
        else:
            logger.info(f"{model.name} full synchronization started.")

        page = 1
        resp = [1]
        total_synced = 0
        while len(resp) > 0:
            resp = list_call(page, 100, modified_since)
            if len(resp) > 0:
                detailed_list = []
                for res in resp:
                    print('.', end='', flush=True)
                    detailed_list.append(details_call(res['id']))
                model.upsert_results([(detailed_list, model.name)])
                page += 1
                total_synced += len(resp)
                print(f"\n{model.name} synced {len(resp)} records", flush=True)

        logger.info(f"Done, synchronized {total_synced} {model.name}")

    def companies_sync(self, full_sync=False):
        """ Syncs teamleader companies into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader companies.
        """
        self.resource_sync(self.tlc.list_companies, self.tlc.get_company,
                           self.companies, full_sync)

    def contacts_sync(self, full_sync=False):
        """ Syncs teamleader contacts into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader contacts.
        """
        self.resource_sync(self.tlc.list_contacts, self.tlc.get_contact,
                           self.contacts, full_sync)

    def custom_fields_sync(self, full_sync=False):
        """ Syncs teamleader custom_fields into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader custom_fields.
        """
        self.resource_sync(self.tlc.list_custom_fields, self.tlc.get_custom_field,
                           self.custom_fields, full_sync)

    def departments_sync(self, full_sync=False):
        """ Syncs teamleader departments into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader departments.
        """
        self.resource_sync(self.tlc.list_departments, self.tlc.get_department,
                           self.departments, full_sync)

    def events_sync(self, full_sync=False):
        """ Syncs teamleader events into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader events.
        """
        self.resource_sync(self.tlc.list_events, self.tlc.get_event,
                           self.events, full_sync)

    def invoices_sync(self, full_sync=False):
        """ Syncs teamleader invoices into target database

            Arguments:
            modified_since -- Filters teamleader results with updated_since
                              If None, it will retrieve all teamleader invoices.
        """
        self.resource_sync(self.tlc.list_invoices, self.tlc.get_invoice,
                           self.invoices, full_sync)

    def projects_sync(self, full_sync=False):
        """ Syncs teamleader projects into target database

            Arguments:
            modified_since -- Filters teamleader projects with updated_since
                              If None, it will retrieve all teamleader projects.
        """
        self.resource_sync(self.tlc.list_projects, self.tlc.get_project,
                           self.projects, full_sync)

    def users_sync(self, full_sync=False):
        """ Syncs teamleader users into target database

            Arguments:
            modified_since -- Filters teamleader users with updated_since
                              If None, it will retrieve all teamleader users.
        """
        self.resource_sync(self.tlc.list_users, self.tlc.get_user,
                           self.users, full_sync)

    def teamleader_sync(self, full_sync=False):
        if full_sync:
            logger.info("Start full sync from teamleader")
        else:
            logger.info("Start delta sync from teamleader")

        self.companies_sync(full_sync)
        self.contacts_sync(full_sync)
        self.custom_fields_sync(full_sync)
        self.departments_sync(full_sync)
        self.events_sync(full_sync)
        self.invoices_sync(full_sync)
        self.projects_sync(full_sync)
        self.users_sync(full_sync)

        logger.info("Teamleader sync completed")

    def teamleader_status(self):
        status = {}
        status['companies'] = self.companies.status()
        status['contacts'] = self.contacts.status()
        status['custom_fields'] = self.custom_fields.status()
        status['departments'] = self.departments.status()
        status['events'] = self.events.status()
        status['invoices'] = self.invoices.status()
        status['projects'] = self.projects.status()
        status['users'] = self.users.status()

        return status

    def csv_path(self):
        return "contacts_export.csv"

    def export_csv(self):
        self.contacts.export_csv(self.csv_path())

    def main(self):
        try:
            argh.dispatch_commands([
                self.companies_sync,
                self.contacts_sync,
                self.custom_fields_sync,
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
