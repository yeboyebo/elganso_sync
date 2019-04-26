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
        result = {}
        status = 200

        if "passwd" in data and data["passwd"] == "bUqfqBMnoH":
            result = task_manager.task_executer("orders_download", data)
        else:
            result = {"msg": "Autorización denegada"}
            status = 401

        return HttpResponse(json.dumps(result), status=status, content_type="application/json")


# @class_declaration download #
class download(elganso_sync_download):
    pass
