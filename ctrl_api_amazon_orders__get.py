import json

from django.http import HttpResponse

from sync.tasks import task_manager


# @class_declaration interna_get #
class interna_get():
    pass


# @class_declaration elganso_sync_get #
from models.flsyncppal import flsyncppal_def as syncppal


class elganso_sync_get(interna_get):

    @staticmethod
    def start(pk, data):
        result = None
        status = None
        if "passwd" in data and data["passwd"] == syncppal.iface.get_param_sincro('apipass')['auth']:
            response = task_manager.task_executer("amazon_orders_get", data)

            result = response["data"]
            status = response["status"]
        else:
            result = {"msg": "Autorización denegada"}
            status = 401

        return HttpResponse(json.dumps(result), status=status, content_type="application/json")


# @class_declaration get #
class get(elganso_sync_get):
    pass
