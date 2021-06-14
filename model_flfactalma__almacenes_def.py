
# @class_declaration elganso_sync #
from models.flsyncppal import flsyncppal_def as syncppal


class elganso_sync(flfactalma):

    params = syncppal.iface.get_param_sincro('apipass')

    def elganso_sync_damelistaalmacenessincro(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:
                lista_almacenes = qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'ALMACENES_SINCRO'")
                if not lista_almacenes:
                    return {"Error": "Petición Incorrecta. No se ha encontrado la lista de almacenes", "status": 10}
                else:
                    return {"almacenes": lista_almacenes}
            else:
                return {"Error": "Petición Incorrecta", "status": 10}
        except Exception as e:
            print(e)
            qsatype.debug(ustr(u"Error inesperado consulta de bono: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def __init__(self, context=None):
        super().__init__(context)

    def damelistaalmacenessincro(self, params):
        return self.ctx.elganso_sync_damelistaalmacenessincro(params)

