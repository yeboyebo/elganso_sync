import json

from django.http import HttpResponse

from sync.tasks import task_manager


# @class_declaration interna_process #
class interna_process():
    pass


# @class_declaration community_sync_process #
from models.flsyncppal import flsyncppal_def as syncppal


class community_sync_process(interna_process):

    @staticmethod
    def start(pk, data):
        result = None
        status = None

        if "passwd" in data and data["passwd"] == syncppal.iface.get_param_sincro('apipass')['auth']:
            response = task_manager.task_executer("mg2_refounds_process", data)
            if response:
                result = response["data"]
                status = response["status"]
        else:
            result = {"msg": "Autenticación denegada"}
            status = 401

        return HttpResponse(json.dumps(result), status=status, content_type="application/json")


# @class_declaration process #
class process(community_sync_process):
    pass
