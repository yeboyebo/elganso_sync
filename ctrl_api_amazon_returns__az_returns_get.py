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
    fecha_sincro = ""
    esquema = "AZ_RETURNS_GET"
    codtienda = "AMAZ"

    def __init__(self, params=None):
        super().__init__("azreturnsget", AmazonDriver(), params)

        self.set_sync_params(self.get_param_sincro('amazon'))

    def get_data(self):
        # return "<AmazonEnvelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"amzn-envelope.xsd\"><Header><DocumentVersion>1.00</DocumentVersion></Header><MessageType>Returns-Report</MessageType><Message><return_details><item_details><item_name>El Ganso 1050s200003 Camisa Casual, Amarillo (Amarillo 0003), X-Large (Tamaño del Fabricante:XL) para Hombre</item_name><asin>B07Y3YBD8J</asin><return_reason_code>AMZ-PG-APP-TOO-SMALL</return_reason_code><merchant_sku>1050s200003-XL</merchant_sku><in_policy>Y</in_policy><return_quantity>1</return_quantity><resolution>StandardRefund</resolution><category>Apparel</category><refund_amount>59.9</refund_amount></item_details><item_details><item_name>El Ganso 1050s200003 Camisa Casual, Amarillo (Amarillo 0003), X-Large (Tamaño del Fabricante:XL) para Hombre</item_name><asin>B07Y3YBD8J</asin><return_reason_code>AMZ-PG-APP-TOO-SMALL</return_reason_code><merchant_sku>1050s200003-XL</merchant_sku><in_policy>Y</in_policy><return_quantity>1</return_quantity><resolution>StandardRefund</resolution><category>Apparel</category><refund_amount>59.9</refund_amount></item_details><order_id>408-9386448-4007569</order_id><order_date>2020-11-03T17:08:47Z</order_date><amazon_rma_id>DJ1XPkq5RRMA</amazon_rma_id><return_request_date>2020-11-12T12:44:17Z</return_request_date><return_request_status>Approved</return_request_status><a_to_z_claim>false</a_to_z_claim><is_prime>N</is_prime><label_details><currency_code>EUR</currency_code><label_cost>0.0</label_cost><label_type>AmazonUnPaidLabel</label_type></label_details><label_to_be_paid_by>Customer</label_to_be_paid_by><return_type>C-Returns</return_type><order_amount>59.9</order_amount><order_quantity>1</order_quantity></return_details></Message></AmazonEnvelope>"

        attr = self.get_attributes()
        signature = self.sign_request(attr)
        url = "https://{}/?{}&Signature={}".format(self.driver.azHost, attr, signature)
        request_report = self.driver.send_request("post", url=url)
        id_report_request = self.procesar_peticion_request_report(request_report)

        if not id_report_request:
            return []

        time.sleep(20)
        attr = self.get_attributes_getreportlist(id_report_request)
        signature = self.sign_request(attr)
        url = "https://{}/?{}&Signature={}".format(self.driver.azHost, attr, signature)
        request_get_report_list = self.driver.send_request("post", url=url)
        id_report = self.procesar_peticion_get_report_list(request_get_report_list)
        if not id_report:
            time.sleep(20)
            request_get_report_list = self.driver.send_request("post", url=url)
            id_report = self.procesar_peticion_get_report_list(request_get_report_list)
        if not id_report:
            return []

        attr = self.get_attributes_getreport(id_report)
        signature = self.sign_request(attr)
        url = "https://{}/?{}&Signature={}".format(self.driver.azHost, attr, signature)
        request_get_report = self.driver.send_request("post", url=url)
        return request_get_report

    def procesar_peticion_request_report(self, request_report):
        response = xml2dict(bytes(request_report, 'utf-8'))
        if not hasattr(response.RequestReportResult.ReportRequestInfo, 'ReportRequestId'):
            self.log("Exito", "No hay datos que sincronizar")
            return False
        return str(response.RequestReportResult.ReportRequestInfo.ReportRequestId)

    def procesar_peticion_get_report_list(self, request_get_report_list):
        response = xml2dict(bytes(request_get_report_list, 'utf-8'))
        if not hasattr(response.GetReportListResult, 'ReportInfo'):
            return False
        return str(response.GetReportListResult.ReportInfo.ReportId)

    def get_attributes(self):
        attributes = self.get_raw_attributes()

        ordered_dict = OrderedDict(sorted(attributes.items()))
        return "&".join(["{}={}".format(key, self.url_encode(value)) for key, value in ordered_dict.items()])

    def get_raw_attributes(self):
        return {
            "Action": "RequestReport",
            "Merchant": self.driver.azMerchant,
            "SignatureVersion": "2",
            "Timestamp": (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "Version": "2009-01-01",
            "SignatureMethod": "HmacSHA256",
            "AWSAccessKeyId": self.driver.azAccessKey,
            "ReportType": "_GET_XML_RETURNS_DATA_BY_RETURN_DATE_",
            "StartDate": self.get_fechasincro(),
            "MarketplaceIdList.Id.1": self.driver.azMarketplaceId
        }

    def get_attributes_getreportlist(self, id_report_request):
        attributes = self.get_raw_attributes_getreportlist(id_report_request)

        ordered_dict = OrderedDict(sorted(attributes.items()))
        return "&".join(["{}={}".format(key, self.url_encode(value)) for key, value in ordered_dict.items()])

    def get_raw_attributes_getreportlist(self, id_report_request):
        return {
            "Action": "GetReportList",
            "Merchant": self.driver.azMerchant,
            "SignatureVersion": "2",
            "Timestamp": (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "Version": "2009-01-01",
            "SignatureMethod": "HmacSHA256",
            "AWSAccessKeyId": self.driver.azAccessKey,
            "ReportRequestIdList.Id.1": id_report_request
        }

    def get_attributes_getreport(self, id_report):
        attributes = self.get_raw_attributes_getreport(id_report)

        ordered_dict = OrderedDict(sorted(attributes.items()))
        return "&".join(["{}={}".format(key, self.url_encode(value)) for key, value in ordered_dict.items()])

    def get_raw_attributes_getreport(self, id_report):
        return {
            "Action": "GetReport",
            "Merchant": self.driver.azMerchant,
            "SignatureVersion": "2",
            "Timestamp": (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "Version": "2009-01-01",
            "SignatureMethod": "HmacSHA256",
            "AWSAccessKeyId": self.driver.azAccessKey,
            "ReportId": id_report
        }

    def get_fechasincro(self):
        fecha = self.dame_fechasincrotienda(self.esquema, self.codtienda)
        if fecha and fecha != "None" and fecha != "":
            self.fecha_sincro = fecha
        else:
            self.fecha_sincro = "2020-11-03T00:00:01Z"

        return self.fecha_sincro

    def dame_fechasincrotienda(self, esquema, codtienda):
        return qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "fechasincro || 'T' || horasincro || 'Z'", "esquema = '{}' AND codtienda = '{}'".format(esquema, codtienda))

    def process_all_data(self, all_data):

        if all_data == []:
            self.log("Exito", "No hay datos que sincronizar")
            if not self.guarda_fechasincrotienda(self.esquema, self.codtienda):
                self.log("Error", "Fallo al guardar fecha última sincro")
                return self.small_sleep
            return False

        response = xml2dict(bytes(all_data, 'utf-8'))

        if not hasattr(response.Message.return_details, 'amazon_rma_id'):
            self.log("Exito", "No hay datos que sincronizar")
            if not self.guarda_fechasincrotienda(self.esquema, self.codtienda):
                self.log("Error", "Fallo al guardar fecha última sincro")
                return self.small_sleep
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

    def sign_request(self, attr):
        string_to_sign = "POST\n{}\n/\n".format(self.driver.azHost) + attr
        return self.url_encode(
            b64encode(
                hmac.new(
                    bytes(self.driver.azSecretKey, 'utf-8'),
                    msg=bytes(string_to_sign, 'utf-8'),
                    digestmod=hashlib.sha256
                ).digest()
            ).decode('utf-8')
        )

    def url_encode(self, param):
        encoded = urllib.parse.quote(param)
        encoded = encoded.replace('/', '%2F')
        return encoded

    def after_sync(self):
        if not self.guarda_fechasincrotienda(self.esquema, self.codtienda):
            self.log("Error", "Fallo al guardar fecha última sincro")
            return self.small_sleep

        if self.idamazon:
            self.log("Exito", "Las siguientes devoluciones se han sincronizado correctamente: {}".format(self.idamazon))
        else:
            self.log("Exito", "No hay datos que sincronizar")

        return self.large_sleep

    def guarda_fechasincrotienda(self, esquema, codtienda):
        ahora = datetime.utcnow()
        hace_un_dia = ahora - timedelta(days=1)
        fecha = str(hace_un_dia)[:10]
        hora = str(hace_un_dia)[11:19]

        idsincro = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "id", "esquema = '{}' AND codtienda = '{}'".format(esquema, codtienda))

        if idsincro:
            qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE id = {}".format(fecha, hora, idsincro))
        else:
            qsatype.FLSqlQuery().execSql("INSERT INTO tpv_fechasincrotienda (codtienda, esquema, fechasincro, horasincro) VALUES ('{}', '{}', '{}', '{}')".format(codtienda, esquema, fecha, hora))

        return True
