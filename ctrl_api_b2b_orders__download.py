import json

from django.http import HttpResponse

from sync.tasks import task_manager


# @class_declaration interna_download #
class interna_download():
    pass


# @class_declaration elganso_sync_download #
class orders_b2b_download(interna_download):

    @staticmethod
    def start(pk, data):
        print("ENTRA")
        result = None
        status = None

        if "passwd" in data and data["passwd"] == "bUqfqBMnoH":
            response = task_manager.task_executer("orders_b2b_download", data)

            result = response["data"]
            status = response["status"]
        else:
            result = {"msg": "Autorización denegada"}
            status = 401

        return HttpResponse(json.dumps(result), status=status, content_type="application/json")


# @class_declaration download #
class download(orders_b2b_download):
    pass
