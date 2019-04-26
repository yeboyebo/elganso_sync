import json

from django.http import HttpResponse

from sync.tasks import task_manager


# @class_declaration interna_upload #
class interna_upload():
    pass


# @class_declaration elganso_sync_upload #
class elganso_sync_upload(interna_upload):

    @staticmethod
    def start(pk, data):
        result = {}
        status = 200

        if "passwd" in data and data["passwd"] == "bUqfqBMnoH":
            result = task_manager.task_executer("points_upload", data)
        else:
            result = {"msg": "Autorización denegada"}
            status = 401

        return HttpResponse(json.dumps(result), status=status, content_type="application/json")


# @class_declaration upload #
class upload(elganso_sync_upload):
    pass
