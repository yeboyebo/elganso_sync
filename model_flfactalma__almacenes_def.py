
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
                    where_talla = " AND s.talla = '" + str(params["talla"]) + "'"

                lista_almacenes = qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'ALMACENES_SINCRO'").split(',')

                where_almacenes = ""
                for idx in range(len(lista_almacenes)):
                    if where_almacenes == "":
                        where_almacenes = "'" + str(lista_almacenes[idx]) + "'"
                    else:
                        where_almacenes += ",'" + str(lista_almacenes[idx]) + "'"

                q = qsatype.FLSqlQuery()
                q.setTablesList("stocks")
                q.setSelect("s.codalmacen,a.nombre,a.direccion,a.provincia,a.codpostal,a.codpais,a.telefono")
                q.setFrom("stocks s INNER JOIN almacenes a ON s.codalmacen = a.codalmacen")
                q.setWhere("s.codalmacen IN (" + where_almacenes + ") AND s.disponible >= 2 AND s.referencia = '" + str(params["sku"]) + "'" + where_talla)

                if not q.exec_():
                    return {"Error": "No hay stock en ningún almacen", "status": -1}

                if not q.size():
                    return {"Error": "No hay stock en ningún almacen", "status": -1}

                lista_almacenes = []
                while(q.next()):
                    lista_almacenes.append({"codAlmacen": q.value("s.codalmacen"), "nombre": q.value("a.nombre"), "direccion": q.value("a.direccion"), "provincia": q.value("a.provincia"), "codpostal": q.value("a.codpostal"), "codpais": q.value("a.codpais"), "telefono": q.value("a.telefono")})

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

