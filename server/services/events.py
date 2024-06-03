import os, shutil, sys, subprocess
import requests

from flask import Flask, Response, request
from flask import stream_with_context

import utils

import json
from urllib.parse import unquote

from database.database import Database
db = Database()

from config import Config
config = Config("config.ini")

from action_manager.action_manager import ActionManager
action_manager = ActionManager()

from common import *

def event_io(message):
    event = message["event"]
    actions = db.bindings.get_actions(event)
    for action in actions:
        action_manager.execute(action)