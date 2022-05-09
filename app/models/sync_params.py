#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#   app/models/sync_params.py
#
#   Teamleader sync parameters used in POST /sync/teamleader call
#
from pydantic import BaseModel, Field


class SyncParams(BaseModel):
    full_sync: bool = Field(
        False,
        description="""
        True:  synchronizes all records.
        False: only synchronizes starting from max last_modified timestamp in database.
        """
    )

    class Config:
        schema_extra = {
            "example": {
                "full_sync": False
            }
        }
