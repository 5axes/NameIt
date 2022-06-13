# Initial Copyright (c)2022 5@xes
# The Name It ! plugin is released under the terms of the AGPLv3 or higher.

from . import NameIt

def getMetaData():
    return {}

def register(app):
    return {"extension": NameIt.NameIt()}
