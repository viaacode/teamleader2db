from fastapi import APIRouter, BackgroundTasks
from typing import Optional
from app.app import App as SyncApp

router = APIRouter()


class JobState:
    def __init__(self):
        self.counter = 0
        self.teamleader_running = False
        self.sync_app = SyncApp()

    @property
    def app(self):
        return self.sync_app

    def teamleader_job(self, full_sync):
        self.teamleader_running = True
        self.sync_app.teamleader_sync(full_sync)
        self.teamleader_running = False


state = JobState()


@router.get("/teamleader")
async def teamleader_sync_status():
    status = {}
    status['companies'] = state.app.companies_status()
    status['contacts'] = state.app.contacts_status()
    #status['departments'] = state.app.contacts_status()
    #status['events'] = state.app.contacts_status()
    #status['invoices'] = state.app.contacts_status()
    #status['projects'] = state.app.contacts_status()
    #status['users'] = state.app.contacts_status()
    status['job_running'] = state.teamleader_running

    return status


@router.post("/teamleader")
async def start_teamleader_sync(
    background_tasks: BackgroundTasks,
    full_sync: Optional[bool] = False
):

    if not state.teamleader_running:
        background_tasks.add_task(state.teamleader_job, full_sync)
        status = 'Teamleader sync started'
    else:
        status = 'Teamleader sync was already running'

    return {
        "status": status,
        "full_sync": full_sync
    }
