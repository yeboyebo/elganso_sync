import json

from django.http import HttpResponse

from sync.tasks import task_manager


# @class_declaration interna_recieve #
class interna_recieve():
    pass

# @class_declaration elganso_sync_recieve #
class elganso_sync_recieve(interna_recieve):

    @staticmethod
    def start(pk, data):
        result = None
        status = None

        if "passwd" in data and data["passwd"] == "bUqfqBMnoH":
            response = task_manager.task_executer("stock_inicial_recieve", data)
            if response:
                result = response["data"]
                status = response["status"]
        else:
            result = {"msg": "Error al sincronizar"}
            status = 401

        return HttpResponse(json.dumps(result), status=status, content_type="application/json")


# @class_declaration recieve #
class recieve(elganso_sync_recieve):
    pass
