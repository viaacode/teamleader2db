#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#   app/models/contacts.py
#
#   Model class to save synced contacts into the postgres database.
#   and also do an export to csv file based on the t_content json blob
#   stored in the database for each contact that has been synced before.
#
from app.comm.psql_wrapper import PostgresqlWrapper
from app.models.sync_model import SyncModel
import csv


class Contacts(SyncModel):
    """Acts as a client to query and modify information from and to database"""

    def __init__(self, db_params: dict, table_names: dict):
        self.table = table_names.get('contacts_table', 'tl_contacts')
        self.name = 'contacts'
        self.postgresql_wrapper = PostgresqlWrapper(db_params)
        self.postgresql_wrapper.execute(
            Contacts.create_table_sql(self.table)
        )

    def parse_or_id(self, contact_json):
        # TODO: map this correctly somehow
        return contact_json.get('or_id')

    def parse_cp_name_catpro(self, contact_json):
        # TODO: map this correctly somehow
        return contact_json.get('cp_name_catpro')

    def parse_email(self, contact_json):
        emails = contact_json.get('emails', [])

        for em in emails:
            if em['type'] == 'primary':
                return em['email']

        # return empty value if not found
        return ''

    def parse_phone(self, contact_json):
        telephones = contact_json.get('telephones', [])
        for p in telephones:
            if p['type'] == 'phone':
                return p['number']

        # return empty value if not found
        return ''

    def parse_website(self, contact_json):
        return contact_json.get('website')

    def parse_form_url(self, contact_json):
        return contact_json.get('web_url')

    def parse_description(self, contact_json):
        # TODO: check if this is correct with Tine
        return contact_json.get('remarks')

    def parse_accountmanager(self, contact_json):
        # TODO: map this correctly somehow
        # i'm guessing this might be companies/position instead which can be
        # Consultant, Account manager, ...?
        return contact_json.get('accountmanager')

    def write_contacts_csv(self, csvfile):
        export = csv.writer(csvfile, delimiter=';', quotechar='"')

        # write header
        export.writerow(
            [
                "or_id", "cp_name_catpro", "email", "phone",
                "website", "form_url", "description", "accountmanager"
            ]
        )

        # write contacts csv export rows based on tl_content json
        batch_size = 100
        total_contacts = self.count()
        export_offset = 0
        export_rows = 0
        print(f"Contacts count in database = {total_contacts}", flush=True)

        while export_offset < total_contacts:
            contact_data = self.select_page(batch_size, export_offset)
            export_offset += batch_size

            for row in contact_data:
                # TODO: make dictionary cursor so we can use row['tl_content'] instead
                contact_json = row[2]

                export.writerow([
                    self.parse_or_id(contact_json),
                    self.parse_cp_name_catpro(contact_json),
                    self.parse_email(contact_json),
                    self.parse_phone(contact_json),
                    self.parse_website(contact_json),
                    self.parse_form_url(contact_json),
                    self.parse_description(contact_json),
                    self.parse_accountmanager(contact_json)
                ])
                export_rows += 1

        print(f"Exported {export_rows} contacts to csv file.", flush=True)

    def export_csv(self, csv_path):
        with open(csv_path, 'w') as csvfile:
            self.write_contacts_csv(csvfile)
