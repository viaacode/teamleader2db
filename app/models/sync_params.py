#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#   app/models/sync.py
#
#   Contact and Company sync parameters
#
from pydantic import BaseModel, Field


class SyncParams(BaseModel):
    full_sync: bool = Field(
        False,
        description="""
        True syns all records.
        False sync records since the modified_since date.
        Setting full_sync to False and not specifying modified_since is allowed
        in this case current_date - 2 days is taken as starting date.
        """
    )

    class Config:
        schema_extra = {
            "example": {
                "full_sync": False
            }
        }
