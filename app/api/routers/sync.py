#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#   app/api/routers/sync.py
#
#   Router to make full and delta syncs and show status of
#   last sync or running sync job
#
from fastapi import APIRouter, BackgroundTasks
from typing import Optional
from app.app import App as SyncApp

router = APIRouter()


class Worker:
    def __init__(self):
        self.teamleader_running = False
        self.sync_app = SyncApp()

    @property
    def app(self):
        return self.sync_app

    def teamleader_job(self, full_sync):
        self.teamleader_running = True
        self.sync_app.teamleader_sync(full_sync)
        self.teamleader_running = False


worker = Worker()


@router.get("/oauth", include_in_schema=False)
def auth_callback(code: str, state: str = ''):
    result = worker.app.auth_callback(code, state)
    return result


@router.get("/teamleader")
async def teamleader_sync_status():
    status = worker.app.teamleader_status()
    status['job_running'] = worker.teamleader_running

    return status


@router.post("/teamleader")
async def start_teamleader_sync(
    background_tasks: BackgroundTasks,
    full_sync: Optional[bool] = False
):

    if not worker.teamleader_running:
        background_tasks.add_task(worker.teamleader_job, full_sync)
        status = 'Teamleader sync started'
    else:
        status = 'Teamleader sync was already running'

    return {
        "status": status,
        "full_sync": full_sync
    }
