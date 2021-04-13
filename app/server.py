#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.api.api import api_router

app = FastAPI(
    title="Teamleader2Db",
    description="API to synchronize Teamleader data to postgres database",
    version="1.0.2",
)

app.include_router(api_router)

config = ConfigParser()
log = logging.get_logger(__name__, config=config)


# make root show the swagger docs (and hide it from the documentation)
@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse("/docs")
