import json

from django.http import HttpResponse

from sync.tasks import task_manager


# @class_declaration interna_download #
class interna_download():
    pass


# @class_declaration elganso_sync_download #
from models.flsyncppal import flsyncppal_def as syncppal


class elganso_sync_download(interna_download):

    @staticmethod
    def start(pk, data):
        result = None
        status = None

        if "passwd" in data and data["passwd"] == syncppal.iface.get_param_sincro('apipass')['auth']:
            if "codtienda" not in data or not data["codtienda"]:
                result = {"msg": "Se requiere un código de tienda"}
                status = 400
            else:
                response = task_manager.task_executer("store_inventarios_download", data)

                result = response["data"]
                status = response["status"]
        else:
            result = {"msg": "Autorización denegada"}
            status = 401

        return HttpResponse(json.dumps(result), status=status, content_type="application/json")


# @class_declaration download #
class download(elganso_sync_download):
    pass
