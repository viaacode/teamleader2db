#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#   app/api/routers/export.py
#
#   Router to handle csv export, export status and download path
#   This exports the contacts synced before on the database into a csv file
#
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse

from app.app import App as SyncApp
from datetime import datetime

router = APIRouter()


class CsvWorker:
    def __init__(self):
        self.export_running = False
        self.last_export = 'Please run an export first with POST /export/export_csv'
        self.sync_app = SyncApp()

    @property
    def app(self):
        return self.sync_app

    def export_job(self):
        self.export_running = True
        self.last_export = 'New contacts export to csv is in progress...'
        self.sync_app.export_csv()
        self.export_running = False
        self.last_export = datetime.now().isoformat()


csvw = CsvWorker()


@router.get("/download_csv")
async def download_csv():
    file_path = csvw.app.csv_path()

    return FileResponse(path=file_path, filename=file_path, media_type='text/csv')


@router.get("/export_status")
async def export_status():
    return {
        "export_running": csvw.export_running,
        "last_export": csvw.last_export
    }


@router.post("/export_csv")
async def export_csv(
    background_tasks: BackgroundTasks,
):

    if not csvw.export_running:
        background_tasks.add_task(csvw.export_job)
        status = 'Contacts csv export started. Check status for completion'
    else:
        status = 'Previous csv export is still running...'

    return {
        "status": status,
    }
