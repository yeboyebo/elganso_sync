
# @class_declaration elganso_sync #
from models.flsyncppal import flsyncppal_def as syncppal


class elganso_sync(flfactalma):

    params = syncppal.iface.get_param_sincro('apipass')

    def elganso_sync_damelistaalmacenessincro(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:

                '''lista_almacenes = qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'ALMACENES_SINCRO'").replace(",", "','")
                print(lista_almacenes)
                if not lista_almacenes:
                    return {"Error": "Petición Incorrecta. No se ha encontrado la lista de almacenes", "status": 10}'''

                #empresasCorner = qsatype.FactoriaModulos.get('flfactppal').iface.listaEmpresaCorner()

                q = qsatype.FLSqlQuery()
                q.setTablesList("tiendas,provincias")
                q.setSelect("t.codtienda,t.latitud,t.longitud,t.descripcion,t.direccion,t.ciudad,p.mg_idprovincia,t.provincia,t.codpostal,t.codpais,t.telefono,t.generotienda")
                q.setFrom("tpv_tiendas t INNER JOIN provincias p ON t.idprovincia = p.idprovincia")
                q.setWhere("t.sincroactiva GROUP BY t.codtienda,t.latitud,t.longitud,t.descripcion,t.direccion,t.ciudad,t.provincia,p.mg_idprovincia,t.codpostal,t.codpais,t.telefono,t.generotienda ORDER BY t.codtienda")

                if not q.exec_():
                    return {"Error": "Falló la consulta", "status": -1}

                if not q.size():
                    return {"Error": "No hay almacenes activas", "status": -2}

                lista_almacenes = []

                while(q.next()):
                        codTienda = q.value("t.codtienda")

                        qGenero = qsatype.FLSqlQuery()
                        qGenero.setTablesList(u"eg_clasificacioncategoria,gruposmoda")
                        qGenero.setSelect(u"g.descripcion")
                        qGenero.setFrom(u"eg_clasificacioncategoria c INNER JOIN gruposmoda g ON c.codgrupomoda = g.codgrupomoda")
                        qGenero.setWhere(ustr(u"c.codtienda = '", codTienda, u"'"))

                        if not qGenero.exec_():
                            return {"Error": "Falló la consulta de genero", "status": -3}

                        listaGenero = ""
                        while(qGenero.next()):
                            listaGenero += qGenero.value("g.descripcion") + "/"

                        lista_almacenes.append({"id": codTienda, "lat": q.value("t.latitud"), "lng": q.value("t.longitud"), "descripcion": q.value("t.descripcion"), "direccion": q.value("t.direccion"), "provincia": q.value("t.provincia"), "idprovincia": q.value("p.mg_idprovincia"), "telefono": q.value("t.telefono"), "codpostal": q.value("t.codpostal"), "ciudad": q.value("t.ciudad"), "codpais": q.value("t.codpais"), "tipo": listaGenero})

                return lista_almacenes
            else:
                return {"Error": "Petición Incorrecta", "status": 10}
        except Exception as e:
            print(e)
            qsatype.debug(ustr(u"Error inesperado consulta de lista de almacenes activos: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def elganso_sync_damealmacenesconstock(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:
                if "sku" not in params:
                    return {"Error": "Formato Incorrecto. Falta el parámetro sku", "status": 10}

                where_talla = ""
                if "talla" in params:
                    if len(str(params["talla"])) > 3:
                        return {"Error": "Formato Incorrecto. Longitud talla no es coherente", "status": 10}
                    if str(params["talla"]) != "None":
                        where_talla = " AND s.talla = '" + str(params["talla"]) + "'"

                empresasCorner = qsatype.FactoriaModulos.get('flfactppal').iface.listaEmpresaCorner()

                q = qsatype.FLSqlQuery()
                q.setTablesList("stocks,tiendas,param_parametros")
                q.setSelect("s.codalmacen,t.descripcion,t.direccion,t.ciudad,t.provincia,t.codpostal,t.codpais,t.telefono, s.talla")
                q.setFrom("tpv_tiendas t inner join stocks s on t.codalmacen = s.codalmacen left outer join param_parametros p on 'RSTOCK_' || t.codalmacen = p.nombre")
                q.setWhere("t.sincroactiva and (p.nombre like 'RSTOCK_%' or p.nombre is null) AND s.disponible > 1 AND s.referencia = '" + str(params["sku"]) + "' AND t.idempresa not in (" + str(empresasCorner) + ")" + where_talla + " GROUP BY s.codalmacen,t.descripcion,t.direccion,t.ciudad,t.provincia,t.codpostal,t.codpais,t.telefono, s.talla ORDER BY s.codalmacen, s.talla")

                if not q.exec_():
                    return {"Error": "No hay stock en ningún almacen", "status": -1}

                if not q.size():
                    return {"Error": "No hay stock en ningún almacen", "status": -2}

                lista_almacenes = []
                cod_almacen_ant = ""

                while(q.next()):
                    if cod_almacen_ant != q.value("s.codalmacen"):
                        tallas = []
                        tallas.append(q.value("s.talla"))
                        lista_almacenes.append({"codAlmacen": q.value("s.codalmacen"), "nombre": q.value("t.descripcion"), "direccion": q.value("t.direccion"), "ciudad": q.value("t.ciudad"), "provincia": q.value("t.provincia"), "codpostal": q.value("t.codpostal"), "codpais": q.value("t.codpais"), "telefono": q.value("t.telefono"), "tallas": tallas})
                    else:
                        tallas = lista_almacenes[len(lista_almacenes) - 1]["tallas"]
                        tallas.append(q.value("s.talla"))

                    cod_almacen_ant = q.value("s.codalmacen")

                return {"almacenes": lista_almacenes}
            else:
                return {"Error": "Petición Incorrecta", "status": 10}
        except Exception as e:
            print(e)
            qsatype.debug(ustr(u"Error inesperado consulta de stock: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def elganso_sync_damedisponibleaweb(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:
                if "sku" not in params and "skus" not in params:
                    return {"Error": "Formato Incorrecto. Falta el parámetro sku o skus si es array", "status": 10}
                referencias = ""
                if "sku" in params:
                    splitted_sku = str(params["sku"]).split("-")

                    if len(splitted_sku) > 0:
                        referencias = referencias + str(splitted_sku[0]) + "','"

                if "skus" in params:
                    for idx in range(len(params["skus"])):
                        sku = params["skus"][idx]
                        splitted_sku = str(sku).split("-")

                        if len(splitted_sku) > 0:
                            referencias = referencias + str(splitted_sku[0]) + "','"

                if referencias == "":
                    return {"Error": "Formato SKU no localizado", "status": 2}

                q = qsatype.FLSqlQuery()
                q.setSelect("referencia,talla,disponible")
                q.setFrom("stocks")
                #q.setWhere("referencia = '" + referencia + "' AND talla <> '" + talla + "' AND codalmacen = 'AWEB' AND disponible > 0 ")
                q.setWhere("referencia IN ('" + referencias + "') AND referencia <> '' AND codalmacen = 'AWEB' AND disponible > 0 ORDER BY referencia, talla")

                if not q.exec_():
                    return {"Error": "Error en la consulta", "status": -1}

                if not q.size():
                    return {"Error": "No hay stock disponible para ninguna talla", "status": -2}

                lista_disponibles = []

                while(q.next()):
                    sku = q.value("referencia")
                    talla = q.value("talla")

                    if talla != "TU":
                        sku = "{}-{}".format(sku, talla)

                    lista_disponibles.append({sku:q.value("disponible")})

                return {"disponible":lista_disponibles}
            else:
                return {"Error": "Petición Incorrecta", "status": 10}
        except Exception as e:
            print(e)
            qsatype.debug(ustr(u"Error inesperado consulta de stock cambio: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def elganso_sync_damestockawebcontrareembolso(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:
                if "skus" not in params:
                    return {"Error": "Formato Incorrecto. Falta el parámetro skus", "status": 10}

                lista_disponibles = []
                for idx in range(len(params["skus"])):
                    sku = params["skus"][idx]

                    splitted_sku = str(sku).split("-")

                    referencia = ""
                    talla = "TU"

                    if len(splitted_sku) == 2:
                        referencia = str(splitted_sku[0])
                        talla = str(splitted_sku[1])
                    elif len(splitted_sku) == 1:
                        referencia = str(splitted_sku[0])
                    else:
                        return {"Error": "Formato del SKU incorrecto", "status": 2}

                    disponible = qsatype.FLUtil.sqlSelect("stocks", "disponible", "referencia = '" + referencia + "' AND talla = '" + talla + "' AND codalmacen = 'AWEB'")

                    if talla != "TU":
                        sku = "{}-{}".format(referencia, talla)

                    lista_disponibles.append({sku:disponible})

                return {"disponible":lista_disponibles}
            else:
                print(params['passwd'])
                print(params['skus'])
                return {"Error": "Petición Incorrecta", "status": 10}
        except Exception as e:
            print(e)
            qsatype.debug(ustr(u"Error inesperado consulta de stock cambio: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def __init__(self, context=None):
        super().__init__(context)

    def damelistaalmacenessincro(self, params):
        return self.ctx.elganso_sync_damelistaalmacenessincro(params)

    def damealmacenesconstock(self, params):
        return self.ctx.elganso_sync_damealmacenesconstock(params)

    def damedisponibleaweb(self, params):
        return self.ctx.elganso_sync_damedisponibleaweb(params)

    def damestockawebcontrareembolso(self, params):
        return self.ctx.elganso_sync_damestockawebcontrareembolso(params)

