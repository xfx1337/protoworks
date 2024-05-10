from singleton import singleton

import exceptions

import pythoncom
from win32com.client import Dispatch, gencache

from environment.software.kompas3d.files import Files

import threading
import time

import utils

#KOMPAS 3D
@singleton
class Api:
    def __init__(self, env):
        self.env = env
        self.api_inited = False
        
        self.iApplication = None
        self.app = None
        self.module = None
        self.consts = None
    
        self.queue = {}
        self.hp_queue = {}
        self.answers = {}

        self.files = Files(self)

    def kompas_api_thread(self):
        pythoncom.CoInitialize()
        self.iApplication = Dispatch('KOMPAS.Application.7')
        self.module = gencache.EnsureModule("{75C9F5D0-B5B8-4526-8681-9903C567D2ED}", 0, 1, 0)
        self.consts = self.module.constants
        self.files.init_api()
        self.current_stream = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch, self.iApplication)
        self.iApplication.HideMessage = self.consts.ksHideMessageNo
        self.api_inited = True

        self.app = self.iApplication

        self.exit = False
        #self.app.Visible = True

        while not self.exit:
            time.sleep(0.1)
            hp_keys = list(self.hp_queue.keys()).copy()
            while len(hp_keys) > 0:
                entry_id = hp_keys[0]
                entry = self.hp_queue[hp_keys[0]]
                if not entry["ask_response"]:
                    entry["fn"]()
                else:
                    answers[entry_id] = entry["fn"]()
                del self.hp_queue[entry_id]

            keys = list(self.queue.keys())
            if len(keys) > 0:
                entry_id = keys[0]
                entry = self.queue[keys[0]]
                if not entry["ask_response"]:
                    entry["fn"]()
                else:
                    self.answers[entry_id] = entry["fn"]()
                del self.queue[entry_id]


    def request(self, fn, ask_response=False, high_priority=False, dont_delete_answer=False):
        request = {"fn": fn, "ask_response": ask_response}
        i = utils.get_unique_id()
        if not high_priority:
            self.queue[i] = request.copy()
        else:
            self.hp_queue[i] = request.copy()
        if ask_response:
            while i not in self.answers:
                time.sleep(0.1)
            if not dont_delete_answer:
                answer = self.answers[i]
                try: answer = answer.copy()
                except: pass
                del self.answers[i]
                return answer
            else:
                return self.answers[i]
