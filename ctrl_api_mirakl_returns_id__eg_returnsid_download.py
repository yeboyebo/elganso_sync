from YBLEGACY import qsatype
import xmltodict
import json
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import tostring
from datetime import datetime, timedelta

from controllers.base.mirakl.returns.controllers.returns_download import ReturnsDownload
from controllers.api.mirakl.returnsnew.serializers.returnnew_serializer import ReturnNewSerializer
from models.flfact_tpv.objects.egreturn_raw import EgReturn
from controllers.base.mirakl.returns.serializers.ew_devolucioneseciweb_serializer import DevolucioneseciwebSerializer
from models.flfact_tpv.objects.ew_devolucioneseciweb_raw import EwDevolucioneseciweb


class EgMiraklReturnsIdDownload(ReturnsDownload):

    id_mirakl = ""
    es_valdemoro = False
    def __init__(self, params=None):
        super().__init__("egmiraklreturnsid", params)

        returns_params = self.get_param_sincro('miraklReturnsIdDownload')
        self.returns_url = returns_params['url']
        self.returns_test_url = returns_params['test_url']

        self.set_sync_params(self.get_param_sincro('mirakl'))

    def get_data(self):
        returns_url = self.returns_url if self.driver.in_production else self.returns_test_url
        self.id_mirakl = qsatype.FLUtil.sqlSelect("eg_devolucioneseciwebptesincronizar", "idmirakl", "sincronizada = FALSE ORDER BY id")
        if self.id_mirakl:
            self.es_valdemoro = qsatype.FLUtil.sqlSelect("eg_devolucioneseciwebptesincronizar", "valdemoro", "idmirakl = '" + self.id_mirakl + "'")

        print(self.id_mirakl)
        result = self.send_request("get", url=returns_url.format(self.id_mirakl))
        return result

    def process_all_data(self, all_data):
        if "messages" not in all_data:
            self.log("Exito", "No hay datos que sincronizar")
            return False

        processData = False
        for data in all_data["messages"]:
            try:
                if "body" not in data:
                    continue

                if str(data["body"]).startswith("<?xml"):
                    continue

                bodyMensaje = str(data["body"])
                bodyMensaje = bodyMensaje.replace("\"", "__aqcomillas__")
                bodyMensaje = bodyMensaje.replace("'", "\"")
                bodyMensaje = bodyMensaje.replace("__aqcomillas__", "'")
                mensajeDevol = json.loads(bodyMensaje)
                fecha = str(data["date_created"])[0:19] + "Z"
                data["date_created"] = fecha

                if "message" not in mensajeDevol:
                    continue
                if "type" not in mensajeDevol['message']:
                    continue
                        
                tipoMsg = str(mensajeDevol['message']['type'])
                if tipoMsg != "R10" and tipoMsg != "R02":
                    continue
                processData = True
                if self.process_data(data):
                    self.success_data.append(data)
            except Exception as e:
                print("exception")
                self.sync_error(data, e)


        if processData == False:
            self.log("Exito", "No hay datos que sincronizar")
            return False

        return True

    def process_data(self, data):
        if not data:
            self.error_data.append(data)
            return False
        #print("PROCESS_DATA: " + str(data))
        idComandaO = qsatype.FLUtil.quickSqlSelect("ew_ventaseciweb", "idtpv_comanda", "idweb = '{}'".format(data["order_id"]))

        bodyMensaje = str(data["body"])
        print("*******BODYMENSAJE 2******: ", bodyMensaje)
        bodyMensaje = bodyMensaje.replace("\"", "__aqcomillas__")
        bodyMensaje = bodyMensaje.replace("'", "\"")
        bodyMensaje = bodyMensaje.replace("__aqcomillas__", "'")
        mensajeDevol = json.loads(bodyMensaje)
        
        for devolucion in mensajeDevol['message']['returns']:
            barcode = str(devolucion["ean"])
            cantidad = float(devolucion["quantity"])
            cantDev = float(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "cantdevuelta", "idtpv_comanda = {} AND barcode = '{}'".format(idComandaO, barcode)))
            if not cantDev or cantDev == "None":
                cantDev = 0

            if cantDev >= cantidad:
                idComanda = qsatype.FLUtil.quickSqlSelect("ew_ventaseciweb v inner join tpv_comandas c on v.idtpv_comanda = c.idtpv_comanda inner join tpv_lineascomanda l on c.idtpv_comanda = l.idtpv_comanda inner join tpv_comandas c2 on c.codigo = c2.codcomandadevol inner join tpv_lineascomanda l2 on c2.idtpv_comanda = l2.idtpv_comanda and l.barcode = l2.barcode left join ew_devolucioneseciweb d on c2.idtpv_comanda = d.idtpv_comanda", "l2.idtpv_comanda", "v.idweb = '{}' AND d.idventaweb IS NULL".format(str(data["order_id"])))
                    
                if idComanda:                    
                    if str(idComanda) != "None":
                        data["valdemoro"] = False
                        eciweb_data = DevolucioneseciwebSerializer().serialize(data)

                        eciweb_data["idtpv_comanda"] = idComanda
                        eciweb_data["datosdevol"] = data["body"]

                        devoleciweb = EwDevolucioneseciweb(eciweb_data)
                        devoleciweb.save()
                    
                        return True
                
                self.log("Error", "La línea con barcode {} de la venta {} ya ha sido procesada".format(barcode, data["order_id"]))
                return False

        data["valdemoro"] = False
        eciweb_data = DevolucioneseciwebSerializer().serialize(data)
        if not eciweb_data:
            self.error_data.append(data)
            return False

        idComanda = self.masAccionesProcessData(eciweb_data)
        if not idComanda or idComanda == "None":
            raise NameError("No se pudo crear la devolucion")

        eciweb_data["idtpv_comanda"] = idComanda
        eciweb_data["datosdevol"] = data["body"]

        devoleciweb = EwDevolucioneseciweb(eciweb_data)

        devoleciweb.save()

        return True

    def masAccionesProcessData(self, eciweb_data):
        eciweb_data["datosdevol"] = json.loads(json.dumps(eciweb_data["datosdevol"]))
        return_data = self.get_return_serializer().serialize(eciweb_data)
        if not return_data:
            return False
        return_data["valdemoro"] = False
        objReturn = EgReturn(return_data)
        objReturn.save()
        idtpvDevol = objReturn.cursor.valueBuffer("idtpv_comanda")
        codComandaDevol = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "codcomandadevol", "idtpv_comanda = '{}'".format(idtpvDevol))
        idtpvVenta = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '{}'".format(codComandaDevol))
        qL = qsatype.FLSqlQuery()
        qL.setSelect("barcode, cantidad")
        qL.setFrom("tpv_lineascomanda")
        qL.setWhere("idtpv_comanda = {}".format(idtpvDevol))
        if not qL.exec_():
            self.log("Error. Fallo la query al obtener los datos de devolución {}".format(idtpvDevol), "egmiraklreturns")
            return False

        while qL.first():
            cantDev = qsatype.FLUtil.sqlSelect("tpv_lineascomanda", "cantdevuelta", "idtpv_comanda = {} AND barcode = '{}'".format(idtpvVenta, qL.value("barcode"))) + (int(qL.value("cantidad")) * -1)
            qsatype.FLSqlQuery().execSql("UPDATE tpv_lineascomanda SET cantdevuelta = '{}' WHERE idtpv_comanda = {} AND barcode = '{}'".format(cantDev, idtpvVenta, qL.value("barcode")))
           
            """if not qsatype.FLUtil.sqlUpdate("tpv_lineascomanda", ["cantdevuelta"], [cantDev], "idtpv_comanda = {} AND barcode = '{}'".format(idtpvVenta, qL.value("barcode"))):
                print("ENTRA EN ESTE FALSE")
                return False"""
        return objReturn.cursor.valueBuffer("idtpv_comanda")

    def get_return_serializer(self):
        return ReturnNewSerializer()

    def after_sync(self):

        qsatype.FLSqlQuery().execSql("UPDATE eg_devolucioneseciwebptesincronizar SET sincronizada = TRUE WHERE idmirakl = '{}'".format(self.id_mirakl))

        if self.es_valdemoro == True:
            self.es_valdemoro = False
            qsatype.FLSqlQuery().execSql("UPDATE ew_devolucioneseciweb SET valdemoro = TRUE WHERE idventaweb = '{}'".format(self.id_mirakl))

        if self.success_data:
            self.log("Exito", "Las siguientes devoluciones se han sincronizado correctamente: {}".format(self.id_mirakl))
            return self.small_sleep

        return self.large_sleep

