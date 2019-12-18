import json

from django.http import HttpResponse

from sync.tasks import task_manager


# @class_declaration interna_download #
class interna_download():
    pass


# @class_declaration elganso_sync_download #
class elganso_sync_download(interna_download):

    @staticmethod
    def start(pk, data):
        result = None
        status = None

        if "passwd" in data and data["passwd"] == "bUqfqBMnoH":
            response = task_manager.task_executer("mirakl_returnsvaldemoroid_download", data)
            result = response["data"]
            status = response["status"]
        else:
            result = {"msg": "Autorización denegada"}
            status = 401

        respuesta = HttpResponse(json.dumps(result), status=status, content_type="application/json")
        return respuesta


# @class_declaration download #
class download(elganso_sync_download):
    pass
