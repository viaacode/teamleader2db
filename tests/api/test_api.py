#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestApi:
    @pytest.fixture
    @patch('app.app.Users')
    @patch('app.app.Projects')
    @patch('app.app.Invoices')
    @patch('app.app.Events')
    @patch('app.app.Departments')
    @patch('app.app.Companies')
    @patch('app.app.Contacts')
    @patch('app.comm.teamleader_client.TeamleaderAuth')
    @patch("app.app.TeamleaderClient")
    def client(self, *mocks):
        from app.server import app
        return TestClient(app)

    def test_teamleader_full_sync(self, client):
        response = client.post("/sync/teamleader?full_sync=true")
        assert response.status_code == 200
        content = response.json()
        assert 'Teamleader sync started' in content['status']

    def test_teamleader_delta_sync(self, client):
        response = client.post("/sync/teamleader?full_sync=false")
        assert response.status_code == 200
        content = response.json()
        assert 'Teamleader sync started' in content['status']

    def test_contact_csv_status(self, client):
        response = client.get("/export/export_status")
        assert response.status_code == 200
        content = response.json()
        assert content['export_running'] == False
        assert 'last_export' not in content
        assert 'Please run an export first with POST /export/export_csv' in content['status']

    def test_contact_csv_export(self, client):
        response = client.post("/export/export_csv")
        assert response.status_code == 200
        content = response.json()
        assert "Contacts csv export started. Check status for completion" in content['status']

    def test_contact_csv_status(self, client):
        response = client.get("/export/export_status")
        assert response.status_code == 200
        content = response.json()
        assert content['export_running'] == False
        assert 'last_export' in content

    def test_contact_csv_download(self, client):
        response = client.get("/export/download_csv")
        assert response.status_code == 200

        assert response.headers['content-type'] == 'text/csv; charset=utf-8'
        assert response.headers['content-disposition'] == 'attachment; filename="contacts_export.csv"'

    def test_health(self, client):
        response = client.get("/health/live")
        assert response.status_code == 200
        assert 'OK' in response.text

    def test_swagger_docs(self, client):
        response = client.get('/')
        content = response.text
        assert 'Teamleader2Db - Swagger UI' in content

    def test_teamleader_status(self, client):
        response = client.get("/sync/teamleader")
        assert response.status_code == 200
