
# @class_declaration elganso_sync #
from sync import tasks


class elganso_sync(flfact_tpv):

    def elganso_sync_mgSyncDevWeb(self, params):
        if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
            tasks.getUnsynchronizedDevWeb.delay(params['fakeRequest'])
            return {"msg": "Tarea encolada correctamente"}
        else:
            print("no tengo contraseña")

        return False

    def __init__(self, context=None):
        super().__init__(context)

    def mgSyncDevWeb(self, params):
        return self.ctx.elganso_sync_mgSyncDevWeb(params)

