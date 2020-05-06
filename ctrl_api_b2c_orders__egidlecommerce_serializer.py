from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class EgIdlEcommerce(DefaultSerializer):

    def get_data(self):
        metodoEnvio = str(self.init_data["shipping_method"])

        if "imagen_recoger" in self.init_data:
            if str(self.init_data["imagen_recoger"]) != "None" and self.init_data["imagen_recoger"] != None and self.init_data["imagen_recoger"] != False:
                metodoEnvio = "i4seur_31_2"

        transIDL = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "transportista", "LOWER(metodoenviomg) = '" + metodoEnvio + "' OR UPPER(metodoenviomg) = '" + metodoEnvio + "' OR metodoenviomg = '" + metodoEnvio + "'")

        if not transIDL:
            return True

        metodoIDL = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "metodoenvioidl", "LOWER(metodoenviomg) = '" + metodoEnvio + "' OR UPPER(metodoenviomg) = '" + metodoEnvio + "' OR metodoenviomg = '" + metodoEnvio + "'")
        esRecogidaTienda = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "recogidaentienda", "LOWER(metodoenviomg) = '" + metodoEnvio + "' OR UPPER(metodoenviomg) = '" + metodoEnvio + "' OR metodoenviomg = '" + metodoEnvio + "'")
        impAlbaran = True
        impFactura = False
        impDedicatoria = False
        esRegalo = False
        emisor = ""
        receptor = ""
        mensajeDedicatoria = ""

        if not esRecogidaTienda and str(self.init_data["gift"]) == "None":
            impAlbaran = False

        if str(self.init_data["gift"]) != "None":
            if "gift_message_id" in self.init_data["gift"]:
                impDedicatoria = True
                esRegalo = True
                emisor = str(self.init_data["gift"]["sender"])
                receptor = str(self.init_data["gift"]["recipient"])
                mensajeDedicatoria = str(self.init_data["gift"]["message"])

        if not esRecogidaTienda:
            if "country_id" in self.init_data["shipping_address"]:
                if str(self.init_data["shipping_address"]["country_id"]) == "ES":
                    if "region_id" in self.init_data["shipping_address"]:
                            esProvinciaFactura = qsatype.FLUtil.sqlSelect("provincias", "imprimirfactura", "mg_idprovincia = " + str(self.init_data["shipping_address"]["region_id"]))
                            if esProvinciaFactura:
                                impFactura = True
                else:
                    imprimirFacturaPais = qsatype.FLUtil.sqlSelect("paises", "imprimirfactura", "codiso = '" + str(self.init_data["shipping_address"]["country_id"]) + "'")
                    if imprimirFacturaPais:
                        impFactura = True

        fecha_prevista_envio = str(self.get_init_value("delayed_shipping_date"))
        if fecha_prevista_envio != "None" and fecha_prevista_envio != "" and fecha_prevista_envio != None:
            self.set_string_value("fechaprevistaenvio", fecha_prevista_envio)

        self.set_string_relation("codcomanda", "codcomanda", max_characters=15)
        if "imagen_recoger" in self.init_data:
            if str(self.init_data["imagen_recoger"]) != "None" and self.init_data["imagen_recoger"] != None and self.init_data["imagen_recoger"] != False:
                self.set_string_value("tipo", 'CAMBIO')
                print("URLL: ", str(self.init_data["imagen_recoger"]))
                self.set_data_relation("urlimagen", "imagen_recoger")
                #self.set_string_value("urlimagen", str(self.init_data["imagen_recoger"]))
        else:
            self.set_string_value("tipo", 'VENTA')
        self.set_string_value("transportista", str(transIDL))
        self.set_string_value("metodoenvioidl", str(metodoIDL))
        self.set_data_value("imprimiralbaran", impAlbaran)
        self.set_data_value("imprimirfactura", impFactura)
        self.set_data_value("imprimirdedicatoria", impDedicatoria)
        self.set_string_value("emisor", str(emisor))
        self.set_string_value("receptor", str(receptor))
        self.set_string_value("mensajededicatoria", str(mensajeDedicatoria))
        self.set_data_value("esregalo", esRegalo)
        self.set_data_value("facturaimpresa", False)
        self.set_data_value("envioidl", False)
        self.set_data_value("numseguimientoinformado", False)
        self.set_data_value("bonocreado", False)
        self.set_string_value("confirmacionenvio", 'No')

        return True
