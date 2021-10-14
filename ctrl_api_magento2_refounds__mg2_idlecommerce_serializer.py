from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class Mg2IdlEcommerce(DefaultSerializer):

    def get_data(self):
        #metodoEnvio = str(self.init_data["carrier"])
        metodoEnvio = "i4seur_31_2"

        transIDL = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "transportista", "LOWER(metodoenviomg) = '" + metodoEnvio + "' OR UPPER(metodoenviomg) = '" + metodoEnvio + "' OR metodoenviomg = '" + metodoEnvio + "'")

        if not transIDL:
            return False

        metodoIDL = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "metodoenvioidl", "LOWER(metodoenviomg) = '" + metodoEnvio + "' OR UPPER(metodoenviomg) = '" + metodoEnvio + "' OR metodoenviomg = '" + metodoEnvio + "'")

        impAlbaran = False
        impFactura = False
        impDedicatoria = False
        esRegalo = False
        emisor = ""
        receptor = ""
        mensajeDedicatoria = ""

        self.set_string_relation("codcomanda", "codcomanda", max_characters=12)
        self.set_string_value("tipo", 'CAMBIO')
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
