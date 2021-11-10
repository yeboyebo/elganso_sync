from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class Mg2ProductsSerializer(DefaultSerializer):

    def get_data(self):
        sku = str(self.init_data["sku"])

        if qsatype.FLUtil.sqlSelect("articulos", "referencia", "referencia = '{}'".format(sku)):
            if not self.actualizar_datos_articulo():
                raise NameError("Error al actualizar los datos del articulo.")
                return False
        else:
            if not self.crear_articulo_web():
                raise NameError("Error al crear el articulo.")
                return False
        return True

    def actualizar_datos_articulo(self):

        curArticulo = qsatype.FLSqlCursor("articulos")
        curArticulo.select("referencia = '" + str(self.init_data["sku"]) + "'")

        if curArticulo.first():
            curArticulo.setModeAccess(curArticulo.Edit)
            curArticulo.refreshBuffer()
            curArticulo.setActivatedCommitActions(False)
            curArticulo.setActivatedCheckIntegrity(False)
            curArticulo.setValueBuffer("descripcion", str(self.init_data["name"]))
            curArticulo.setValueBuffer("peso", str(self.init_data["weight"]))
            for custom_attributes in self.init_data["custom_attributes"]:
                if str(custom_attributes["attribute_code"]) == "description":
                    curArticulo.setValueBuffer("mgdescripcion", str(custom_attributes["value"]))

                if str(custom_attributes["attribute_code"]) == "short_description":
                    curArticulo.setValueBuffer("mgdescripcioncorta", str(custom_attributes["value"]))

                if str(custom_attributes["attribute_code"]) == "composicion_textil":
                    curArticulo.setValueBuffer("egcomposicion", str(custom_attributes["value"]))

                if str(custom_attributes["attribute_code"]) == "lavado":
                    curArticulo.setValueBuffer("egsignoslavado", str(custom_attributes["value"]))

                if str(custom_attributes["attribute_code"]) == "sexo":
                    cod_grupo_moda = qsatype.FLUtil.sqlSelect("gruposmoda", "codgrupomoda", "descripcion = '{}'".format(str(custom_attributes["value"])))
                    if cod_grupo_moda:
                        curArticulo.setValueBuffer("codgrupomoda", cod_grupo_moda)

                if str(custom_attributes["attribute_code"]) == "gruporemarketing":
                    cod_tipo_prenda = qsatype.FLUtil.sqlSelect("tiposprenda", "codtipoprenda", "gruporemarketing = '{}'".format(str(custom_attributes["value"])))
                    if cod_tipo_prenda:
                        curArticulo.setValueBuffer("codtipoprenda", cod_tipo_prenda)

                if str(custom_attributes["attribute_code"]) == "color":
                    cod_color = qsatype.FLUtil.sqlSelect("indicessincrocatalogo", "valor", "tipo = 'colores' AND indicecommunity = '{}'".format(custom_attributes["value"]))
                    if cod_tipo_prenda:
                        curArticulo.setValueBuffer("egcolor", cod_color)

                if str(custom_attributes["attribute_code"]) == "season":
                    cod_temporada = qsatype.FLUtil.sqlSelect("indicessincrocatalogo", "valor", "tipo = 'temporadas' AND indicecommunity = '{}'".format(str(custom_attributes["value"])))
                    if cod_temporada:
                        curArticulo.setValueBuffer("codtemporada", self.get_dametemporada(cod_temporada))
                        curArticulo.setValueBuffer("anno", self.get_dameanno(cod_temporada))
            if not curArticulo.commitBuffer():
                raise NameError("Error al actualizar el articulo.")
                return False

        if not self.control_stock_articulo_web():
            return False

        if not self.control_precio_articulo_web():
            return False

        return True

    def get_dametemporada(self, valor):
        valor = valor.split("-")
        temporada = valor[1]

        if temporada == "OI":
            temporada = "W"
        elif temporada == "PV":
            temporada = "s"
        else:
            temporada = "ATEMP"

        return temporada

    def get_dameanno(self, valor):
        valor = valor.split("-")

        return valor[0][2:4]

    def control_stock_articulo_web(self):
        referencia = str(self.init_data["sku"])
        cod_almacen = str(self.init_data["almacen"])

        talla = ""
        for configurable_product_options in self.init_data["configurable_product_options"]:
            for sizes in configurable_product_options["values"]:

                talla = qsatype.FLUtil.sqlSelect("indicessincrocatalogo", "valor", "tipo = 'tallas' AND indicecommunity = '{}'".format(sizes["value_index"]))

                disponible = qsatype.FLUtil.sqlSelect("stocks", "disponible", "referencia = '{}' AND talla = '{}' AND codalmacen = '{}'".format(str(referencia), str(talla), str(cod_almacen)))

                if parseFloat(disponible) != parseFloat(sizes["qty"]):
                    if not self.crear_linearegstock(referencia, talla, parseFloat(sizes["qty"]), cod_almacen):
                        raise NameError("Error al crear la linea de regularizacion.")
                        return False
        return True

    def control_precio_articulo_web(self):
        referencia = str(self.init_data["sku"])
        price = str(self.init_data["price"])
        id_storeview = str(self.init_data["idstoreview"])
        cod_tarifa = qsatype.FLUtil.sqlSelect("mg_storeviews", "codtarifa", "idmagento = {}".format(id_storeview))

        if qsatype.FLUtil.sqlSelect("articulostarifas", "pvp", "referencia = '{}' AND codtarifa = '{}'".format(str(referencia), str(cod_tarifa))):
            qsatype.FLSqlQuery().execSql("UPDATE articulostarifas SET pvp = {} WHERE referencia = '{}' AND codtarifa = '{}'".format(price, referencia, cod_tarifa))
        else:
            qsatype.FLSqlQuery().execSql("UPDATE articulos SET pvp = {} WHERE referencia = '{}'".format(price, referencia))

        return True

    def crear_linearegstock(self, refArticulo, talla, qty, cod_almacen):

        id_stock = qsatype.FLUtil.sqlSelect("stocks", "idstock", "referencia = '{}' AND talla = '{}' AND codalmacen = '{}'".format(str(refArticulo), str(talla), str(cod_almacen)))
        barCode = qsatype.FLUtil.sqlSelect("atributosarticulos", "barcode", "referencia = '{}' AND talla = '{}'".format(str(refArticulo), str(talla)))
        if not id_stock:
            oArticulo = {}
            oArticulo["referencia"] = refArticulo
            oArticulo["barcode"] = barCode
            id_stock = qsatype.FactoriaModulos.get('flfactalma').iface.crearStock(cod_almacen, oArticulo)
            if not id_stock or str(id_stock) == "None":
                raise NameError("No se ha encontrado idstock para el barcode: " + str(barCode))
                return False

        curLineaRegStock = qsatype.FLSqlCursor("lineasregstocks")
        curLineaRegStock.setModeAccess(curLineaRegStock.Insert)
        curLineaRegStock.refreshBuffer()
        curLineaRegStock.setValueBuffer("idstock", id_stock)
        curLineaRegStock.setValueBuffer("fecha", qsatype.Date())
        curLineaRegStock.setValueBuffer("hora", str(qsatype.Date())[-8:])
        curLineaRegStock.setValueBuffer("cantidadini", qsatype.FLUtil.sqlSelect("stocks", "cantidad", "idstock = {}".format(id_stock)))
        curLineaRegStock.setValueBuffer("cantidadfin", qty)
        curLineaRegStock.setValueBuffer("barcode", barCode)
        curLineaRegStock.setValueBuffer("referencia", refArticulo)
        curLineaRegStock.setValueBuffer("talla", talla)

        if not curLineaRegStock.commitBuffer():
            return False

        return True

    def crear_articulo_web(self):

        curArticulo = qsatype.FLSqlCursor("articulos")
        curArticulo.setModeAccess(curArticulo.Insert)
        curArticulo.refreshBuffer()
        curArticulo.setActivatedCommitActions(False)
        curArticulo.setActivatedCheckIntegrity(False)
        curArticulo.setValueBuffer("referencia", str(self.init_data["sku"]))
        curArticulo.setValueBuffer("aw_almacenminpedido", 1)
        curArticulo.setValueBuffer("egtipo", "Producto")
        curArticulo.setValueBuffer("codimpuesto", "GEN")
        curArticulo.setValueBuffer("descripcion", str(self.init_data["name"]))
        curArticulo.setValueBuffer("secompra", True)
        curArticulo.setValueBuffer("curvatallajepropia", True)

        for custom_attributes in self.init_data["custom_attributes"]:
            if str(custom_attributes["attribute_code"]) == "description":
                curArticulo.setValueBuffer("mgdescripcion", str(custom_attributes["value"]))

            if str(custom_attributes["attribute_code"]) == "short_description":
                curArticulo.setValueBuffer("mgdescripcioncorta", str(custom_attributes["value"]))

            if str(custom_attributes["attribute_code"]) == "composicion_textil":
                curArticulo.setValueBuffer("egcomposicion", str(custom_attributes["value"]))

            if str(custom_attributes["attribute_code"]) == "lavado":
                curArticulo.setValueBuffer("egsignoslavado", str(custom_attributes["value"]))

            if str(custom_attributes["attribute_code"]) == "sexo":
                cod_grupo_moda = qsatype.FLUtil.sqlSelect("gruposmoda", "codgrupomoda", "descripcion = '{}'".format(str(custom_attributes["value"])))
                if cod_grupo_moda:
                    curArticulo.setValueBuffer("codgrupomoda", cod_grupo_moda)

            if str(custom_attributes["attribute_code"]) == "gruporemarketing":
                cod_tipo_prenda = qsatype.FLUtil.sqlSelect("tiposprenda", "codtipoprenda", "gruporemarketing = '{}'".format(str(custom_attributes["value"])))
                if cod_tipo_prenda:
                    curArticulo.setValueBuffer("codtipoprenda", cod_tipo_prenda)

            if str(custom_attributes["attribute_code"]) == "color":
                cod_color = qsatype.FLUtil.sqlSelect("indicessincrocatalogo", "valor", "tipo = 'colores' AND indicecommunity = '{}'".format(custom_attributes["value"]))
                if cod_tipo_prenda:
                    curArticulo.setValueBuffer("egcolor", cod_color)

            if str(custom_attributes["attribute_code"]) == "season":
                cod_temporada = qsatype.FLUtil.sqlSelect("indicessincrocatalogo", "valor", "tipo = 'temporadas' AND indicecommunity = '{}'".format(str(custom_attributes["value"])))
                if cod_temporada:
                    curArticulo.setValueBuffer("codtemporada", self.get_dametemporada(cod_temporada))
                    curArticulo.setValueBuffer("anno", self.get_dameanno(cod_temporada))

        curArticulo.setValueBuffer("pvp", str(self.init_data["price"]))
        curArticulo.setValueBuffer("peso", str(self.init_data["weight"]))
        curArticulo.setValueBuffer("stockcomp", False)
        curArticulo.setValueBuffer("mghabilitadoh", True)
        curArticulo.setValueBuffer("aw_plazoentregaprov", "1")
        curArticulo.setValueBuffer("aw_almacenmultiplopedido", "1")
        curArticulo.setValueBuffer("activo", True)
        curArticulo.setValueBuffer("mgvisibilidad", True)
        curArticulo.setValueBuffer("mghabilitado", True)
        curArticulo.setValueBuffer("aw_pedidomin", "1")
        curArticulo.setValueBuffer("egincluircatmagento", False)
        curArticulo.setValueBuffer("mgvisibilidadh", True)
        curArticulo.setValueBuffer("emperchado", False)
        curArticulo.setValueBuffer("aw_multiplopedido", "1")
        curArticulo.setValueBuffer("ivaincluido", True)
        curArticulo.setValueBuffer("mgvisibleweb", True)

        if not qsatype.FactoriaModulos.get('flfactppal').iface.pub_controlDatosMod(curArticulo):
            return False

        if not curArticulo.commitBuffer():
            raise NameError("Error al crear la cabecera del articulo.")
            return False

        if not self.crear_atributosarticulos():
            raise NameError("Error al crear los barcodes del articulo.")
            return False

        if not self.crear_articulostarifas():
            raise NameError("Error al crear el articulo en la tarifa indicada.")
            return False

        if not self.crear_articulosprov():
            raise NameError("Error al crear el articulo en la tarifa indicada.")
            return False

        return True

    def crear_atributosarticulos(self):
        referencia = str(self.init_data["sku"])
        talla = ""

        qsatype.FactoriaModulos.get('formRecordarticulos').iface.ultimoBarcode_ = False
        qsatype.FactoriaModulos.get('formRecordarticulos').iface.calculoBarcode_ = qsatype.FactoriaModulos.get('flfactalma').iface.pub_valorDefectoAlmacen("calculobarcode")
        qsatype.FactoriaModulos.get('formRecordarticulos').iface.digitosBarcode_ = qsatype.FactoriaModulos.get('flfactalma').iface.pub_valorDefectoAlmacen("digitosbarcode")
        qsatype.FactoriaModulos.get('formRecordarticulos').iface.prefijoBarcode_ = qsatype.FactoriaModulos.get('flfactalma').iface.pub_valorDefectoAlmacen("prefijobarcode")

        for configurable_product_options in self.init_data["configurable_product_options"]:
            for sizes in configurable_product_options["values"]:

                talla = qsatype.FLUtil.sqlSelect("indicessincrocatalogo", "valor", "tipo = 'tallas' AND indicecommunity = '{}'".format(sizes["value_index"]))

                curAtrArticulo = qsatype.FLSqlCursor("atributosarticulos")
                curAtrArticulo.setModeAccess(curAtrArticulo.Insert)
                curAtrArticulo.refreshBuffer()
                curAtrArticulo.setValueBuffer("color", "U")
                curAtrArticulo.setValueBuffer("referencia", referencia)
                curAtrArticulo.setValueBuffer("talla", talla)
                curAtrArticulo.setValueBuffer("barcode", qsatype.FactoriaModulos.get('formRecordarticulos').iface.pub_obtenerBarcode(referencia, talla, "U"))

                if not curAtrArticulo.commitBuffer():
                    return False

                if not self.crear_linearegstock(referencia, talla, parseFloat(sizes["qty"]), str(self.init_data["almacen"])):
                    raise NameError("Error al crear la linea de regularizacion.")
                    return False

        return True

    def crear_articulostarifas(self):
        id_storeview = str(self.init_data["idstoreview"])
        cod_tarifa = qsatype.FLUtil.sqlSelect("mg_storeviews", "codtarifa", "idmagento = {}".format(id_storeview))

        curArtTarifa = qsatype.FLSqlCursor("articulostarifas")
        curArtTarifa.setModeAccess(curArtTarifa.Insert)
        curArtTarifa.refreshBuffer()
        curArtTarifa.setValueBuffer("pvp", str(self.init_data["price"]))
        curArtTarifa.setValueBuffer("referencia", str(self.init_data["sku"]))
        curArtTarifa.setValueBuffer("sincronizado", True)
        curArtTarifa.setValueBuffer("codtarifa", cod_tarifa)

        if not curArtTarifa.commitBuffer():
            return False

        return True

    def crear_articulosprov(self):
        nombre_proveedor = str(self.init_data["proveedor"])
        cod_proveedor = qsatype.FLUtil.sqlSelect("proveedores", "codproveedor", "nombre = '{}'".format(nombre_proveedor))

        if not cod_proveedor:
            raise NameError("No se encuentra el proveedor para el articulo.")
            return False

        curArtProveedor = qsatype.FLSqlCursor("articulosprov")
        curArtProveedor.setModeAccess(curArtProveedor.Insert)
        curArtProveedor.refreshBuffer()
        curArtProveedor.setValueBuffer("codproveedor", str(cod_proveedor))
        curArtProveedor.setValueBuffer("requiereembalajes", False)
        curArtProveedor.setValueBuffer("nombre", nombre_proveedor)
        curArtProveedor.setValueBuffer("referencia", str(self.init_data["sku"]))
        curArtProveedor.setValueBuffer("coddivisa", "EUR")

        if not curArtProveedor.commitBuffer():
            return False

        return True
