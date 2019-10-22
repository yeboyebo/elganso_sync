from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from datetime import datetime
import time

from models.flsyncppal import flsyncppal_def as syncppal
from controllers.base.default.serializers.default_serializer import DefaultSerializer
from controllers.api.mirakl.returns.serializers.return_line_serializer import ReturnLineSerializer
from controllers.api.mirakl.returns.serializers.idl_ecommercedevoluciones_serializer import IdlEcommerceDevolucionesSerializer
from controllers.base.mirakl.orders.serializers.order_payment_serializer import OrderPaymentSerializer
from controllers.base.mirakl.orders.serializers.cashcount_serializer import CashCountSerializer

class ReturnSerializer(DefaultSerializer):

    def get_data(self):
        # TMP. Comprobacion de si ya existe??

        # Buscamos la venta original
        qC = qsatype.FLSqlQuery()
        qC.setSelect("c.*")
        qC.setFrom("tpv_comandas c INNER JOIN ew_ventaseciweb v on c.idtpv_comanda = v.idtpv_comanda")
        qC.setWhere("v.idweb = '{}'".format(self.init_data["idventaweb"]))
        if not qC.exec_():
            syncppal.iface.log("Error. Falló la query al obtener los datos de la venta original para {}".format(self.init_data["idventaweb"]), "egmiraklreturns")
            return False

        if not qC.first():
            syncppal.iface.log("Error. No se encontró la venta original para {}".format(self.init_data["idventaweb"]), "egmiraklreturns")
            return False

        codigo = self.get_codigo()
        self.set_string_value("codigo", codigo, max_characters=15)

        codtienda = self.get_codtienda()
        codalmacen = qsatype.FLUtil.quickSqlSelect("tpv_tiendas", "codalmacen", "codtienda = '{}'".format(codtienda))
        punto_venta = qsatype.FLUtil.sqlSelect("tpv_puntosventa", "codtpv_puntoventa", "codtienda = '{}'".format(codtienda))
        
        self.set_string_value("codtpv_puntoventa", punto_venta)
        self.set_string_value("codalmacen", codalmacen)
        self.set_string_value("codtienda", codtienda)
        self.set_string_value("codcomandadevol", str(qC.value("c.codigo")))
        self.set_string_value("tipodoc", "DEVOLUCION")

        # TMP. Codigo agente
        self.set_string_value("codtpv_agente", "0350")
        self.set_data_value("editable", True)
        self.set_data_value("tasaconv", 1)
        self.set_data_value("ptesincrofactura", False)

        utcCreatedDtate = datetime.strptime(self.get_init_value("date_created"), '%Y-%m-%dT%H:%M:%SZ')
        localCreatedDate = self.utcToLocal(utcCreatedDtate)
        fecha = str(localCreatedDate)[:10]
        hora = str(localCreatedDate)[-8:]
        self.set_string_value("fecha", fecha)
        self.set_string_value("hora", hora)

        self.set_string_value("codpostal", "-")
        self.set_string_value("ciudad", "-")
        self.set_string_value("provincia", "-")
        self.set_string_value("codpais", str(qC.value("c.codpais")))
        self.set_string_value("telefono1", "-")
        self.set_string_value("nombrecliente", str(qC.value("c.nombrecliente")))
        self.set_string_relation("direccion", "datosdevol//Mensaje//Recogida//direccionRecogida", max_characters=100)
        self.set_string_value("codserie", self.get_codserie())

        codejercicio = fecha = str(localCreatedDate)[:4]
        self.set_string_value("codejercicio", codejercicio)
        self.set_string_value("codpago", self.get_codpago(), max_characters=10)
        self.set_string_value("egcodfactura", "NULL")

        if "lines" not in self.data["children"]:
            self.data["children"]["lines"] = []

        total = 0
        neto = 0
        itemA = self.init_data["datosdevol"]["Mensaje"]["Devolucion"]
        if str(type(itemA)) == "<class 'list'>":
            for item in itemA:
                if "EAN" not in item:
                    return False

                item.update({
                	"codalmacen": codalmacen,
                    "codcomanda": codigo,
                    "idcomandaO": str(qC.value("c.idtpv_comanda"))
                })

                line_data = ReturnLineSerializer().serialize(item)
                total = total + line_data["pvptotaliva"]
                neto = neto + line_data["pvptotal"]
                self.data["children"]["lines"].append(line_data)
        else:
            if "EAN" not in itemA:
                return False

            itemA.update({
            	"codalmacen": codalmacen,
                "codcomanda": codigo,
                "idcomandaO": str(qC.value("c.idtpv_comanda"))
            })
            line_data = ReturnLineSerializer().serialize(itemA)
            total = total + line_data["pvptotaliva"]
            neto = neto + line_data["pvptotal"]
            self.data["children"]["lines"] = line_data

        new_init_data = self.init_data.copy()
        new_init_data.update({
            "codcomanda": codigo,
            "fecha": self.data["fecha"]
        })

        self.set_data_value("total", total)
        self.set_data_value("neto", neto)
        self.set_data_value("totaliva", total - neto)

        if self.init_data["valdemoro"] == False:
            self.set_string_value("estado", "Abierta")
            self.set_data_value("pagado", 0)
            self.set_data_value("pendiente", total)

            idl_ecommerceDev = IdlEcommerceDevolucionesSerializer().serialize(new_init_data)
            self.data["children"]["idl_ecommercedevoluciones"] = idl_ecommerceDev
        else:
            self.set_string_value("estado", "Cerrada")
            self.set_data_value("pagado", total)
            self.set_data_value("pendiente", 0)

            if "payments" not in self.data["children"]:
                self.data["children"]["payments"] = []

            arqueo_web = CashCountSerializer().serialize(self.data)
            new_data = self.data.copy()
            new_data.update({"idarqueo": arqueo_web["idtpv_arqueo"]})
            pago_web = OrderPaymentSerializer().serialize(new_data)

            if "skip" in arqueo_web and arqueo_web["skip"]:
                arqueo_web = False
            self.data["children"]["cashcount"] = arqueo_web

            self.data["children"]["payments"].append(pago_web)

        return True

    def get_fecha(self):
        fecha = str(self.init_data["date_created"])[:10]
        return fecha

    def get_codtienda(self):
        return "AEVV"

    def get_codserie(self):
        pais = self.data["codpais"]
        codpostal = self.data["codpostal"]

        codpais = None
        codserie = "A"
        codpostal2 = None

        if not pais or pais == "":
            return codserie

        codpais = qsatype.FLUtil.quickSqlSelect("paises", "codpais", "UPPER(codpais) = '{}'".format(pais.upper()))
        if not codpais or codpais == "":
            return codserie

        if codpais != "ES":
            codserie = "X"
        elif codpostal and codpostal != "":
            codpostal2 = codpostal[:2]
            if codpostal2 == "35" or codpostal2 == "38" or codpostal2 == "51" or codpostal2 == "52":
                codserie = "X"

        return codserie

    def get_codejercicio(self):
        date = self.init_data["date_created"][:10]
        splitted_date = date.split("-")

        return splitted_date[0]

    def get_hora(self):
        hour = self.init_data["date_created"][-9:-1]
        hour = "23:59:59" if hour == "00:00:00" else hour
        return hour

    def get_codpago(self):
        return "TARJ"

    def get_codigo(self):
        prefix = "EDV"
        ultima_vta = None

        id_ultima = qsatype.FLUtil.sqlSelect("tpv_comandas", "codigo", "codigo LIKE '{}%' ORDER BY codigo DESC LIMIT 1".format(prefix))

        if id_ultima:
            ultima_vta = parseInt(str(id_ultima)[-(12 - len(prefix)):])
        else:
            ultima_vta = 0

        ultima_vta = ultima_vta + 1

        return "{}{}".format(prefix, qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(ultima_vta), 12 - len(prefix)))

    def utcToLocal(self, utc_datetime):
        now_timestamp = time.time()
        offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
        return utc_datetime + offset