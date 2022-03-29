from YBLEGACY import qsatype
from YBLEGACY.constantes import *
import json

from controllers.base.default.serializers.default_serializer import DefaultSerializer

class Mg2DirectOrdersPendingSerializer(DefaultSerializer):
    cod_almacenes = ""
    barcodes_lineas = ""
    barcodes_con_stock = 0
    def get_data(self):
        if not self.actualizar_items_lineas():
            return False

        if not self.distribucion_almacenes():
            return False

        print("ITEMS_ ", self.init_data["items"])
        return True

    def get_splitted_sku(self, refArticulo):
        return refArticulo.split("-")

    def get_referencia(self, refArticulo):
        return self.get_splitted_sku(refArticulo)[0]

    def distribucion_almacenes(self):
        jsonDatos = self.init_data

        almacenes = self.dame_almacenes(jsonDatos)
        print("ALMACENES FINAL: ", almacenes)
   
        def puntua_combinacion(combinacion):
            puntos = 100000 * self.puntos_productos_disponibles(combinacion)
            puntos += 10000 * self.puntos_cantidad_almacenes(combinacion, almacenes)
            puntos += 1000 * self.puntos_almacen_local(jsonDatos, combinacion)
            puntos += 100 * self.puntos_prioridad(combinacion, almacenes)
            puntos += 10 * self.puntos_bajo_limite(combinacion, almacenes)
            return puntos

        combinaciones = self.combinaciones_almacenes(almacenes)
        if len(combinaciones) == 0:
            return True

        combinaciones_ordenadas = sorted(combinaciones, key=puntua_combinacion, reverse=False)
        mejor_combinacion = combinaciones_ordenadas[0]
        print("MEJOR COMBINACION: ", mejor_combinacion)
        lineas_data = jsonDatos["items"]
        disponibles = self.disponibles_x_almacen(mejor_combinacion)

        for linea in lineas_data:
            barcode = linea["barcode"]
            for almacen in mejor_combinacion:
                clave_disp = self.clave_disponible(almacen, barcode)
                can_disponible = disponibles.get(clave_disp, 0)
                if can_disponible > 0:
                    disponibles[clave_disp] -= 1
                    linea["almacen"] = almacen["cod_almacen"]
                    linea["emailtienda"] = almacen["emailtienda"]
                    linea["barcode"] = barcode
                    if not self.crearLineaEcommerceExcluida(linea):
                        return False

        if not self.crearRegistroEcommerce():
            return False;

        return True

    def dame_almacenes(self, jsonDatos):

        q = qsatype.FLSqlQuery()
        q.setSelect(u"p.nombre, p.valor, a.codpais")
        q.setFrom(u"param_parametros p INNER JOIN almacenes a ON p.nombre = 'RSTOCK_' || a.codalmacen ")
        q.setWhere(u"p.nombre like 'RSTOCK_%'")

        q.exec_()

        if not q.size():
            return True

        margen_almacenes = {}
        pais_almacenes = {}
        
        ref_regalo = qsatype.FLUtil.quickSqlSelect("param_parametros", "valor", "nombre = 'ART_REGALOWEB'")
        
        aRegalo = ref_regalo.split(",")
        paramRegalo = False
        if len(aRegalo) > 0:
            paramRegalo = True
            
        esRegalo = False
        
        lineas_data = self.init_data["items"]
        
        barcodes = []
        lineas = {}

        for linea_data in lineas_data:
            esRegalo = False
            referencia = self.get_referencia(linea_data["sku"])
            
            if paramRegalo:
                for i in range(len(aRegalo)):
                    if str(aRegalo[i][1:-1]) == str(referencia):
                        esRegalo = True

            if not esRegalo:
                barcode = linea_data["barcode"]
                barcodes.append(barcode)
                lineas[barcode] = linea_data["cantidad"]

        while q.next():
            margen_almacenes[str(q.value(u"p.nombre"))] = int(q.value(u"p.valor"))
            pais_almacenes[str(q.value(u"p.nombre"))] = str(q.value(u"a.codpais"))

        almacenes_canales = self.get_almacenes_canales_web()
        print("Almacenes get: ", almacenes_canales)
        almacenes = []
        # combinaciones_almacen = {}
        indice_limite = 0
        limite_sobrepasado = False
        for indice in range (len(almacenes_canales)):
            almacen = almacenes_canales[indice]
            limite_sobrepasado = False
            limite_pedido_minimo = qsatype.FLUtil.quickSqlSelect("param_parametros", "valor", "nombre = 'LPEDIDO_" + almacen["source_code"] + "'")
            if not limite_pedido_minimo:
                limite_pedido_minimo = 1000

            pedidos_almacen = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "COUNT(*)", "fecha = CURRENT_DATE AND codigo like 'WEB%' and codtienda in ('AWEB','AWCL') and idtpv_comanda in (select c.idtpv_comanda from eg_lineasecommerceexcluidas le inner join tpv_lineascomanda l on le.idtpv_linea = l.idtpv_linea inner join tpv_comandas c on (l.idtpv_comanda = c.idtpv_comanda and le.codcomanda = c.codigo) WHERE le.codalmacen = '" + almacen["source_code"] + "' and c.fecha = CURRENT_DATE AND c.codigo like 'WEB%' and c.codtienda in ('AWEB','AWCL') group by c.idtpv_comanda)")

            # limite_sobrepasado = int(pedidos_almacen) >= int(limite_pedido_minimo)
            if int(pedidos_almacen) >= int(limite_pedido_minimo):
                limite_sobrepasado = True
                indice_limite += len(almacenes)


            q = qsatype.FLSqlQuery()
            q.setSelect(u"barcode, disponible")
            q.setFrom(u"stocks")
            q.setWhere(u"codalmacen = '" + almacen["source_code"] + "' AND barcode IN ('" + "', '".join(barcodes) + "') ORDER BY barcode")

            q.exec_()

            if not q.size():
                continue

            jBarcodes = {}
            cant_disponible = 0
            hay_disponible = False
            # mi_combinacion = str(limite_sobrepasado)
            while q.next():                
                #margen = margen_almacenes.get("RSTOCK_" + almacen["source_code"], 0)
                margen = 0
                cant_disponible = q.value("disponible") - margen
                if cant_disponible <= 0:
                    continue
                hay_disponible = True
                jBarcodes[q.value("barcode")] = cant_disponible
                # mi_combinacion += q.value("barcode") + "-" + str(cant_disponible) + ";"


            #if hay_disponible and mi_combinacion not in combinaciones_almacen:
            if hay_disponible:
                # combinaciones_almacen[mi_combinacion] = True
                if self.cod_almacenes == "":
                    self.cod_almacenes = "'" + almacen["source_code"] + "'"
                else:
                    self.cod_almacenes += ",'" + almacen["source_code"] + "'"

                if limite_sobrepasado:
                    almacenes.append({
                        "cod_almacen": almacen["source_code"],
                        "emailtienda": almacen["email"],
                        "total": 0,
                        "lineas": {},
                        "prioridad": 0.99 - indice_limite * 0.01,
                        "codpais": almacen["country_id"],
                        "bajo_limite": limite_pedido_minimo,
                        "disponibles": jBarcodes
                    })
                else:
                    almacenes.append({
                        "cod_almacen": almacen["source_code"],
                        "emailtienda": almacen["email"],
                        "total": 0,
                        "lineas": {},
                        "prioridad": 0.99 - indice * 0.01,
                        "codpais": almacen["country_id"],
                        "bajo_limite": limite_pedido_minimo,
                        "disponibles": jBarcodes
                    })

        self.barcodes_con_stock = qsatype.FLUtil.quickSqlSelect("atributosarticulos", "COUNT(*)", "barcode IN (SELECT barcode FROM stocks WHERE disponible > 0 AND codalmacen IN ({}) AND barcode IN ({}) AND referencia NOT IN ({}) GROUP BY barcode)".format(self.cod_almacenes, self.barcodes_lineas, ref_regalo))

        return almacenes

    def clave_disponible(self, almacen, barcode):
        return almacen["cod_almacen"] + "_X_" + barcode

    def disponibles_x_almacen(self, combinacion):
        disponibles = {}
        for almacen in combinacion:
            for barcode in almacen["disponibles"]:
                disponibles[self.clave_disponible(almacen, barcode)] = almacen["disponibles"][barcode]

        return disponibles

    def puntos_productos_disponibles(self, combinacion):
        lineas = self.init_data["items"]
        max_puntos = len(lineas)
        if len(lineas) > self.barcodes_con_stock:
            max_puntos = len(lineas) - (len(lineas) - self.barcodes_con_stock)
        total_disponible = 0
        disponibles = self.disponibles_x_almacen(combinacion)
        for linea in lineas:
            barcode = linea["barcode"]
            for almacen in combinacion:
                clave_disp = self.clave_disponible(almacen, barcode)
                can_disponible = disponibles.get(self.clave_disponible(almacen, barcode), 0)
                if can_disponible > 0:
                    disponibles[clave_disp] -= 1
                    total_disponible += 1
                    break

        result = total_disponible * 10 / max_puntos
        return result

    def puntos_cantidad_almacenes(self, combinacion, almacenes):
        max_puntos = len(almacenes)
        puntos = len(almacenes) - len(combinacion) + 1
        result = puntos * 10 / max_puntos
        return result

    def puntos_almacen_local(self, jsonDatos, combinacion):
        def es_local(pais):
            return pais == qsatype.FLUtil.quickSqlSelect("pedidoscli", "codpais", "codigo = '{}'".format(jsonDatos["codpedido"]))

        max_puntos = len(combinacion)
        puntos = 0
        for i in range(len(combinacion)):
            puntos += 1 if es_local(combinacion[i]["codpais"]) else 0

        result = puntos * 10 / max_puntos
        return result

    def puntos_prioridad(self, combinacion, almacenes):
        max_puntos = 0
        for almacen in almacenes:
            max_puntos += almacen["prioridad"]

        prioridad = 0
        total_almacenes = len(almacenes)
        for almacen in combinacion:
            prioridad += total_almacenes - almacen["prioridad"]

        result = prioridad * 10 / max_puntos
        return result

    def puntos_bajo_limite(self, combinacion, almacenes):
        max_puntos = len(almacenes)
        puntos = 0

        for almacen in combinacion:
            puntos += 1 if parseFloat(almacen["bajo_limite"]) > 0 else 0

        result = puntos * 10 / max_puntos

        return result

    def combinacion_viable(self, combinacion):
        puntos = self.puntos_productos_disponibles(combinacion)
        return puntos == 10

    def combinaciones_almacenes(self, almacenes):
        from itertools import combinations
        result = []
        for can_almacenes in range(1, len(almacenes) + 1):
        # for can_almacenes in range(1, 4):
            combinaciones = combinations(almacenes, can_almacenes)
            hay_viables = False
            for c in combinaciones:
                if self.combinacion_viable(c):
                    hay_viables = True
                    result.append(c)

            if hay_viables:
                break
                
        return result

    def actualizar_items_lineas(self):
        self.barcodes_lineas = ""
        for linea in self.init_data["items"]:
            if self.barcodes_lineas == "":
                self.barcodes_lineas = "'" + linea["barcode"] + "'"
            else:
                self.barcodes_lineas += ",'" + linea["barcode"] + "'"
        return True

    def get_almacenes_canales_web(self):

        codtienda = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "codtienda", "codigo = '{}'".format(self.init_data["codcomanda"]))
        print("CODTIENDA_ : ", codtienda)
        lista_canales = qsatype.FLUtil.quickSqlSelect("param_parametros", "valor", "nombre = 'LISTA_CANALESWEB'")
        print("lista_canales_ : ", lista_canales)
        jCanalesWeb = qsatype.FLUtil.quickSqlSelect("param_parametros", "valor", "nombre = 'CANALES_WEB'")
        print("jCanalesWeb : ", jCanalesWeb)

        oCanalesWeb = json.loads(str(jCanalesWeb))
        aListaCanales = lista_canales.split(",")
        aCanales = ""
        cod_canal = ""
        for j in range(len(aListaCanales)):
            if aListaCanales[j] in oCanalesWeb:
                aCanales = oCanalesWeb[aListaCanales[j]].split(",")
                for i in range(len(aCanales)):
                    if(codtienda == aCanales[i]):
                        cod_canal = aListaCanales[j]
                        print("CANAL: ", cod_canal)

        almacenes = []
        if cod_canal in oCanalesWeb:
            print(oCanalesWeb[cod_canal])
            aCanales = oCanalesWeb[cod_canal].split(",")
            print(aCanales)
            for c in range(len(aCanales)):
                almacenes.append({"source_code" : aCanales[c], "email": "prueba@gmail.com", "country_id" : qsatype.FLUtil.quickSqlSelect("almacenes", "codpais", "codalmacen = '{}'".format(aCanales[c]))})
        return almacenes

    def crearLineaEcommerceExcluida(self, aDatos):
        print("ENTRA EN crearLineaEcommerceExcluida")

        if str(aDatos["almacen"]) == "AWEB":
            return True

        curLineaEcommerce = qsatype.FLSqlCursor("eg_lineasecommerceexcluidas")
        curLineaEcommerce.setModeAccess(curLineaEcommerce.Insert)
        curLineaEcommerce.refreshBuffer()
        curLineaEcommerce.setValueBuffer("codalmacen", str(aDatos["almacen"]))
        curLineaEcommerce.setValueBuffer("email", str(aDatos["emailtienda"]))
        curLineaEcommerce.setValueBuffer("codcomanda", self.init_data["codcomanda"])
        curLineaEcommerce.setValueBuffer("viajecreado", False)
        curLineaEcommerce.setValueBuffer("correoenviado", False)
        curLineaEcommerce.setValueBuffer("faltantecreada", False)
      
        for linea_data in self.init_data["items"]:
            if str(linea_data["barcode"]) == str(aDatos["barcode"]):
                curLineaEcommerce.setValueBuffer("idtpv_linea", linea_data["idtpv_linea"])

        if not curLineaEcommerce.commitBuffer():
            return False
        return True