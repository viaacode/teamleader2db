#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestApi:
    @pytest.fixture
    @patch('app.app.Companies')
    @patch('app.app.Contacts')
    @patch("app.app.TeamleaderClient")
    def client(self, mock_companies, mock_contacts, mock_tl):
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
