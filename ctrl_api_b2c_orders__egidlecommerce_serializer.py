from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class EgIdlEcommerce(DefaultSerializer):

    def get_data(self):
        metodoEnvio = str(self.init_data["shipping_method"])

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

        self.set_string_relation("codcomanda", "codcomanda", max_characters=12)
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
        self.set_string_value("confirmacionenvio", 'No')

        return True
