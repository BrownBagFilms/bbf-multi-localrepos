# -*- coding: utf-8 -*-


# psutil does not work with maya
def get_psutil(engine_name):
    if engine_name == "tk-maya":
        return None
    from . import psutil
    return psutil
