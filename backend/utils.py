import sys
import traceback

def process_exception(e):
    error = {}
    if isinstance(e, Exception):
        error['title'] = str(e)
        error['details']=traceback.format_tb(e.__traceback__, 100)
    else:
        error['title'] = "Unknown error"
        error['details'] = "no details are available at this time."

    return error

