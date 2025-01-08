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


class EgMiraklReturnsNewDownload(ReturnsDownload):

    fecha_sincro = ""
    esquema = "DEVOLSNEW_ECI_WEB"
    codtienda = "AEVV"

    def __init__(self, params=None):
        super().__init__("egmiraklreturnsnew", params)

        returns_params = self.get_param_sincro('miraklReturnsNewDownload')
        self.returns_url = returns_params['url']
        self.returns_test_url = returns_params['test_url']

        self.set_sync_params(self.get_param_sincro('mirakl'))

    def get_data(self):
        returns_url = self.returns_url if self.driver.in_production else self.returns_test_url
        fecha = self.dame_fechasincrotienda(self.esquema, self.codtienda)
        if fecha and fecha != "None" and fecha != "":
            self.fecha_sincro = fecha
        else:
            self.fecha_sincro = "2024-01-26T00:00:01Z"

        #print("Fecha Sincro: " + self.fecha_sincro)
        # Tmp. Para pruebas. Quitar en producción
        # self.fecha_sincro = "2021-08-30T00:00:01Z"
        result = self.send_request("get", url=returns_url.format(self.fecha_sincro))
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
                # print("*******BODYMENSAJE 1******: ", bodyMensaje)
                bodyMensaje = bodyMensaje.replace("\"", "__aqcomillas__")
                bodyMensaje = bodyMensaje.replace("'", "\"")
                bodyMensaje = bodyMensaje.replace("__aqcomillas__", "'")
                mensajeDevol = json.loads(bodyMensaje)
                fecha = str(data["date_created"])[0:19] + "Z"
                data["date_created"] = fecha
                #print("Fecha JSON: " + fecha)
                if self.fecha_sincro != "":
                    if fecha > self.fecha_sincro:
                        self.fecha_sincro = fecha
                else:
                    self.fecha_sincro = fecha
                #print("Fecha JSON 2: " + self.fecha_sincro)
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

        if not self.guarda_fechasincrotienda(self.esquema, self.codtienda):
            self.log("Error", "Falló al guardar fecha última sincro")
            return self.small_sleep

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
                
                # select c2.codigo, l2.idtpv_comanda from ew_ventaseciweb v inner join tpv_comandas c on v.idtpv_comanda = c.idtpv_comanda inner join tpv_lineascomanda l on c.idtpv_comanda = l.idtpv_comanda inner join tpv_comandas c2 on c.codigo = c2.codcomandadevol inner join tpv_lineascomanda l2 on c2.idtpv_comanda = l2.idtpv_comanda and l.barcode = l2.barcode left join ew_devolucioneseciweb d on c2.idtpv_comanda = d.idtpv_comanda where v.idweb = '00100900698008920240714121918_1-A' and d.idventaweb is null;
                    
                if idComanda:                    
                    if str(idComanda) != "None":
                        # print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: " + str(data["order_id"]) + " idComanda:" + str(idComanda))
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
            if not qsatype.FLUtil.sqlUpdate("tpv_lineascomanda", ["cantdevuelta"], [cantDev], "idtpv_comanda = {} AND barcode = '{}'".format(idtpvVenta, qL.value("barcode"))):
                return False
        return objReturn.cursor.valueBuffer("idtpv_comanda")

    def get_return_serializer(self):
        return ReturnNewSerializer()

    def after_sync(self):
        if not self.guarda_fechasincrotienda(self.esquema, self.codtienda):
            self.log("Error", "Falló al guardar fecha última sincro")
            return self.small_sleep

        if self.success_data:
            self.log("Exito", "Las siguientes devoluciones se han sincronizado correctamente: {}".format([order["order_id"] for order in self.success_data]))

        return self.large_sleep

    def guarda_fechasincrotienda(self, esquema, codtienda):
        print("guarda")
        fecha = str(self.fecha_sincro)[:10]

        fechaSeg = datetime.strptime(self.fecha_sincro, '%Y-%m-%dT%H:%M:%SZ')
        #fecha1Seg = fechaSeg + timedelta(seconds=1)
        fecha5Minutos = fechaSeg - timedelta(minutes=5)
        
        hora = str(fecha5Minutos)[11:19]

        #idsincro = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "id", "esquema = '{}' AND codtienda = '{}'".format(esquema, codtienda))
        qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE esquema = '{}' AND codtienda = '{}'".format(fecha, hora, esquema, codtienda))
        # if idsincro:
            # qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE id = {}".format(fecha, hora, idsincro))
        # else:
            # qsatype.FLSqlQuery().execSql("INSERT INTO tpv_fechasincrotienda (codtienda, esquema, fechasincro, horasincro) VALUES ('{}', '{}', '{}', '{}')".format(codtienda, esquema, fecha, hora))

        return True

    def dame_fechasincrotienda(self, esquema, codtienda):
        return qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "fechasincro || 'T' || horasincro || 'Z'", "esquema = '{}' AND codtienda = '{}'".format(esquema, codtienda))
