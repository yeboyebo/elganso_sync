import hmac
import hashlib
import urllib.parse
import time
import json
from lxml import etree
import xmltodict
from base64 import b64encode

from YBLEGACY import qsatype
from YBLEGACY.constantes import xml2dict

from datetime import datetime, timedelta
from abc import ABC
from collections import OrderedDict

from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.api.amazon.drivers.amazon import AmazonDriver
from controllers.api.amazon.returns.serializers.return_serializer import ReturnSerializer
from models.flfact_tpv.objects.azreturn_raw import AzReturn


class AzReturnsResultGet(DownloadSync, ABC):

    idamazon = None

    def __init__(self, params=None):
        
        self.ids = ""
        super().__init__("azreturnsget", AmazonDriver(), params)
        self.set_sync_params(self.get_param_sincro('amazon'))
        
    def get_data(self):
        # return "<AmazonEnvelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"amzn-envelope.xsd\"><Header><DocumentVersion>1.00</DocumentVersion></Header><MessageType>Returns-Report</MessageType><Message><return_details><item_details><item_name>El Ganso 1050s200003 Camisa Casual, Amarillo (Amarillo 0003), X-Large (Tamaño del Fabricante:XL) para Hombre</item_name><asin>B07Y3YBD8J</asin><return_reason_code>AMZ-PG-APP-TOO-SMALL</return_reason_code><merchant_sku>1050s200003-XL</merchant_sku><in_policy>Y</in_policy><return_quantity>1</return_quantity><resolution>StandardRefund</resolution><category>Apparel</category><refund_amount>59.9</refund_amount></item_details><item_details><item_name>El Ganso 1050s200003 Camisa Casual, Amarillo (Amarillo 0003), X-Large (Tamaño del Fabricante:XL) para Hombre</item_name><asin>B07Y3YBD8J</asin><return_reason_code>AMZ-PG-APP-TOO-SMALL</return_reason_code><merchant_sku>1050s200003-XL</merchant_sku><in_policy>Y</in_policy><return_quantity>1</return_quantity><resolution>StandardRefund</resolution><category>Apparel</category><refund_amount>59.9</refund_amount></item_details><order_id>408-9386448-4007569</order_id><order_date>2020-11-03T17:08:47Z</order_date><amazon_rma_id>DJ1XPkq5RRMA</amazon_rma_id><return_request_date>2020-11-12T12:44:17Z</return_request_date><return_request_status>Approved</return_request_status><a_to_z_claim>false</a_to_z_claim><is_prime>N</is_prime><label_details><currency_code>EUR</currency_code><label_cost>0.0</label_cost><label_type>AmazonUnPaidLabel</label_type></label_details><label_to_be_paid_by>Customer</label_to_be_paid_by><return_type>C-Returns</return_type><order_amount>59.9</order_amount><order_quantity>1</order_quantity></return_details></Message></AmazonEnvelope>"

        q = qsatype.FLSqlQuery()
        q.setSelect("id, xmlreport")
        q.setFrom("az_solicitudesreportsdevoluciones")
        q.setWhere("xmlreport IS NOT NULL AND reportdocumentidprocesado = TRUE AND xmlprocesado = FALSE ORDER BY id LIMIT 1")

        q.exec_()

        if not q.size():
            return []
        
        reports = self.fetch_query(q)
        xmlReport = []
        for row in reports:            
            if self.ids == "":
                self.ids = str(row['id'])
            else:
                self.ids += "," + str(row['id'])

            xmlReport = row['xmlreport']
            
            xmlReport = xmlReport.replace('"', '\"')
        return xmlReport

    def process_all_data(self, all_data):
        if all_data == []:
            self.log("Exito", "No hay datos que sincronizar")
            return False

        response = xml2dict(bytes(all_data, 'utf-8'))

        if not hasattr(response.Message.return_details, 'amazon_rma_id'):
            self.log("Exito", "No hay datos que sincronizar")
            return False

        for devolucion in response.Message.return_details:
            idAmazon = qsatype.FLUtil.sqlSelect("az_ventasamazon", "idamazon", "idamazon = '{}'".format(devolucion.order_id))
            if not idAmazon:
                raise NameError("No se ha localizado el pedido original {}".format(idAmazon))
                return False

            existeDevolucion = qsatype.FLUtil.sqlSelect("az_devolucionesamazon", "iddevolucionamazon", "iddevolucionamazon = '{}'".format(devolucion.amazon_rma_id))
            if not existeDevolucion:
                qsatype.FLSqlQuery().execSql("INSERT INTO az_devolucionesamazon (fechaalta, horaalta, idventaamazon, iddevolucionamazon, datosdevolucion) VALUES (CURRENT_DATE,CURRENT_TIME,'{}','{}','{}')".format(idAmazon, devolucion.amazon_rma_id, etree.tostring(devolucion).decode('utf-8')))

                idComandaDevol = self.process_data(devolucion)
                if idComandaDevol:
                    self.success_data.append(devolucion)
                    qsatype.FLSqlQuery().execSql("UPDATE az_devolucionesamazon SET idtpv_comanda = {} WHERE iddevolucionamazon = '{}'".format(idComandaDevol, devolucion.amazon_rma_id))

                if not self.idamazon:
                    self.idamazon = str(devolucion.amazon_rma_id)
                else:
                    self.idamazon = ',' + (devolucion.amazon_rma_id)

        return True

    def process_data(self, devolucion):
        idComandaO = qsatype.FLUtil.quickSqlSelect("az_ventasamazon", "idtpv_comanda", "idamazon = '{}'".format(devolucion.order_id))

        for linea_devolucion in devolucion.item_details:
            barcode = str(linea_devolucion.merchant_sku)
            cantidad = float(linea_devolucion.return_quantity)
            cantDev = float(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "cantdevuelta", "idtpv_comanda = {} AND barcode = '{}'".format(idComandaO, barcode)))
            if not cantDev or cantDev == "None":
                cantDev = 0

            if cantDev >= cantidad:
                self.log("Error", "La línea con barcode {} de la venta {} ya ha sido procesada".format(barcode, devolucion.order_id))
                return False

        bodyMensaje = str(etree.tostring(devolucion).decode('utf-8'))
        bodyMensaje = bodyMensaje.replace("\"", "__aqcomillas__")
        bodyMensaje = bodyMensaje.replace("'", "\"")
        bodyMensaje = bodyMensaje.replace("__aqcomillas__", "'")
        data = json.loads(json.dumps(xmltodict.parse(bodyMensaje)))

        return_data = self.get_return_serializer().serialize(data["return_details"])
        if not return_data:
            return False

        objReturn = AzReturn(return_data)
        objReturn.save()
        return objReturn.cursor.valueBuffer("idtpv_comanda")

    def get_return_serializer(self):
        return ReturnSerializer()

    def after_sync(self):
        qsatype.FLSqlQuery().execSql("UPDATE az_solicitudesreportsdevoluciones SET xmlprocesado = TRUE WHERE id IN ({})".format(self.ids))

        if self.idamazon:
            self.log("Exito", "Las siguientes devoluciones se han sincronizado correctamente: {}".format(self.idamazon))
        else:
            self.log("Exito", "No hay datos que sincronizar")

        return self.large_sleep

    def fetch_query(self, q):
        field_list = [field.strip() for field in q.select().split(",")]

        rows = []
        while q.next():
            row = {field: q.value(field) for (field) in field_list}
            rows.append(row)
        return rows
        
