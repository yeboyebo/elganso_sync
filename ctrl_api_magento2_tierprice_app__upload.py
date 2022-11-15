import json

from django.http import HttpResponse

from sync.tasks import task_manager


# @class_declaration interna_upload #
class interna_upload():
    pass


# @class_declaration elganso_sync_upload #
from models.flsyncppal import flsyncppal_def as syncppal


class elganso_sync_upload(interna_upload):

    @staticmethod
    def start(pk, data):
        result = None
        status = None

        if "passwd" in data and data["passwd"] == syncppal.iface.get_param_sincro('apipass')['auth']:
            response = task_manager.task_executer("mg2_tierprice_app_upload", data)

            result = response["data"]
            status = response["status"]
        else:
            result = {"msg": "Autorización denegada"}
            status = 401

        return HttpResponse(json.dumps(result), status=status, content_type="application/json")


# @class_declaration upload #
class upload(elganso_sync_upload):
    pass
