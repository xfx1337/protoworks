import pythoncom
from win32com.client import Dispatch, gencache

iApplication = Dispatch('KOMPAS.Application.7')
module = gencache.EnsureModule("{75C9F5D0-B5B8-4526-8681-9903C567D2ED}", 0, 1, 0)
consts = module.constants

breakpoint()