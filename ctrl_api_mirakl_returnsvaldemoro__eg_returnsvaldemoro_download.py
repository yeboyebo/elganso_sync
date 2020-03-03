from abc import ABC
from YBLEGACY import qsatype
import json
import xmltodict
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import tostring

from controllers.base.mirakl.returnsvaldemoro.controllers.returnsvaldemoro_download import ReturnsValdemoroDownload
from controllers.api.mirakl.returns.serializers.return_serializer import ReturnSerializer
from models.flfact_tpv.objects.egreturn_raw import EgReturn
from controllers.base.mirakl.returns.serializers.ew_devolucioneseciweb_serializer import DevolucioneseciwebSerializer
from models.flfact_tpv.objects.ew_devolucioneseciweb_raw import EwDevolucioneseciweb


class EgMiraklReturnsValdemoroDownload(ReturnsValdemoroDownload, ABC):

    def __init__(self, params=None):
        super().__init__("egmiraklreturnsvaldemoro", params)

        returns_params = self.get_param_sincro('miraklReturnsValdemoroDownload')
        self.returns_url = returns_params['url']
        self.returns_test_url = returns_params['test_url']

        self.set_sync_params(self.get_param_sincro('mirakl'))

    def process_data(self, data):
        if not data:
            self.error_data.append(data)
            return False
        
        idComandaO = qsatype.FLUtil.quickSqlSelect("ew_ventaseciweb", "idtpv_comanda", "idweb = '{}'".format(data["order_id"]))

        root = ET.fromstring(data["body"])
        for devolucion in root.findall('Devolucion'):
            barcode = str(devolucion.find("EAN").text)[2:15]
            cantidad = int(devolucion.find("unidades").text)
            cantDev = int(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "cantdevuelta", "idtpv_comanda = {} AND barcode = '{}'".format(idComandaO, barcode)))
            if not cantDev or cantDev == "None":
                cantDev = 0

            if cantDev >= cantidad:
                self.log("Error", "La línea con barcode {} de la venta {} ya ha sido procesada".format(barcode, data["order_id"]))
                return False
            
        data["valdemoro"] = True
        eciweb_data = DevolucioneseciwebSerializer().serialize(data)
        if not eciweb_data:
            self.error_data.append(data)
            return False
        
        idComanda = self.masAccionesProcessData(eciweb_data)
        if not idComanda or idComanda == "None":
            raise NameError("No se pudo crear la devolución")
        
        eciweb_data["idtpv_comanda"] = idComanda
        eciweb_data["datosdevol"] = data["body"]
        
        devoleciweb = EwDevolucioneseciweb(eciweb_data)
        
        devoleciweb.save()
        
        return True

    def masAccionesProcessData(self, eciweb_data):
        print("entra masAccionesProcessData")
        eciweb_data["datosdevol"] = json.loads(json.dumps(xmltodict.parse(eciweb_data["datosdevol"])))
        return_data = self.get_return_serializer().serialize(eciweb_data)

        if not return_data:
            return False

        return_data["valdemoro"] = True
        objReturn = EgReturn(return_data)
        objReturn.save()

        idtpvDevol = objReturn.cursor.valueBuffer("idtpv_comanda");
        codComandaDevol= qsatype.FLUtil.quickSqlSelect("tpv_comandas", "codcomandaDevol", "idtpv_comanda = '{}'".format(idtpvDevol))
        idtpvVenta = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '{}'".format(codComandaDevol))
        
        qL = qsatype.FLSqlQuery()
        qL.setSelect("barcode, cantidad")
        qL.setFrom("tpv_lineascomanda")
        qL.setWhere("idtpv_comanda = {}".format(idtpvDevol))
        
        if not qL.exec_():
            syncppal.iface.log("Error. Falló la query al obtener los datos de devolución {}".format(idtpvDevol), "egmiraklreturnsvaldemoro")
            return False
        
        while qL.first():
            cantDev = qsatype.FLUtil.sqlSelect("tpv_lineascomanda", "cantdevuelta", "idtpv_comanda = {} AND barcode = '{}'".format(idtpvVenta, qL.value("barcode"))) + (int(qL.value("cantidad"))*-1)
            if not qsatype.FLUtil.sqlUpdate("tpv_lineascomanda", ["cantdevuelta"], [cantDev], "idtpv_comanda = {} AND barcode = '{}'".format(idtpvVenta, qL.value("barcode"))):
                return False

        return objReturn.cursor.valueBuffer("idtpv_comanda")

    def get_return_serializer(self):
        return ReturnSerializer()
