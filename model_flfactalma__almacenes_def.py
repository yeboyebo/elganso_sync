
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

    def elganso_sync_damealmacenesconstock(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:
                if "sku" not in params:
                    return {"Error": "Formato Incorrecto. Falta el parámetro sku", "status": 10}
                if "talla" not in params:
                    return {"Error": "Formato Incorrecto. Falta el parámetro talla", "status": 10}

                where_talla = ""
                if str(params["talla"]) != "None":
                    where_talla = " AND talla = '" + str(params["talla"]) + "'"

                lista_almacenes = qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'ALMACENES_SINCRO'").split(',')

                where_almacenes = ""
                for idx in range(len(lista_almacenes)):
                    if where_almacenes == "":
                        where_almacenes = "'" + str(lista_almacenes[idx]) + "'"
                    else:
                        where_almacenes += ",'" + str(lista_almacenes[idx]) + "'"

                q = qsatype.FLSqlQuery()
                q.setTablesList("stocks")
                q.setSelect("codalmacen")
                q.setFrom("stocks")
                q.setWhere("codalmacen IN (" + where_almacenes + ") AND disponible >= 2 AND referencia = '" + str(params["sku"]) + "'" + where_talla)
                if not q.exec_():
                    return {"Error": "No hay stock en ningún almacen", "status": -1}

                if not q.size():
                    return {"Error": "No hay stock en ningún almacen", "status": -1}

                lista_almacenes = ""
                while(q.next()):
                    if lista_almacenes == "":
                        lista_almacenes = q.value("codalmacen")
                    else:
                        lista_almacenes += "," + q.value("codalmacen")

                return {"almacenes": lista_almacenes}
            else:
                return {"Error": "Petición Incorrecta", "status": 10}
        except Exception as e:
            print(e)
            qsatype.debug(ustr(u"Error inesperado consulta de stock: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def __init__(self, context=None):
        super().__init__(context)

    def damelistaalmacenessincro(self, params):
        return self.ctx.elganso_sync_damelistaalmacenessincro(params)

    def damealmacenesconstock(self, params):
        return self.ctx.elganso_sync_damealmacenesconstock(params)

