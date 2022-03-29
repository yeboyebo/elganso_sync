import hmac
import hashlib
import urllib.parse
from lxml import etree

from base64 import b64encode

from YBLEGACY import qsatype
from YBLEGACY.constantes import xml2dict

from datetime import datetime, timedelta
from abc import ABC
from collections import OrderedDict

from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.api.amazon.drivers.amazon import AmazonDriver


class AzOrdersResultGet(DownloadSync, ABC):

    idamazon = None
    fecha_sincro = ""
    esquema = "AZ_ORDERS_GET"
    codtienda = "AMAZ"

    def __init__(self, params=None):
        super().__init__("azordersget", AmazonDriver(), params)

        self.set_sync_params(self.get_param_sincro('amazon'))

    def get_data(self):
        attr = self.get_attributes()
        signature = self.sign_request(attr)
        url = "https://{}/Orders/2013-09-01?{}&Signature={}".format(self.driver.azHost, attr, signature)
        return self.driver.send_request("post", url=url)

    def get_attributes(self):
        attributes = self.get_raw_attributes()

        ordered_dict = OrderedDict(sorted(attributes.items()))
        return "&".join(["{}={}".format(key, self.url_encode(value)) for key, value in ordered_dict.items()])

    def get_raw_attributes(self):
        return {
            "Action": "ListOrders",
            "AWSAccessKeyId": self.driver.azAccessKey,
            "SellerId": self.driver.azMerchant,
            "SignatureVersion": "2",
            "Timestamp": (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "Version": "2013-09-01",
            "SignatureMethod": "HmacSHA256",
            "CreatedAfter": self.get_fechasincro(),
            "MarketplaceId.Id.1": self.driver.azMarketplaceId
        }

    def get_fechasincro(self):
        fecha = self.dame_fechasincrotienda(self.esquema, self.codtienda)
        if fecha and fecha != "None" and fecha != "":
            self.fecha_sincro = fecha
        else:
            self.fecha_sincro = "2020-12-21T00:00:01Z"

        return self.fecha_sincro

    def dame_fechasincrotienda(self, esquema, codtienda):
        return qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "fechasincro || 'T' || horasincro || 'Z'", "esquema = '{}' AND codtienda = '{}'".format(esquema, codtienda))

    def process_all_data(self, all_data):
        response = xml2dict(bytes(all_data, 'utf-8'))
        if not hasattr(response.ListOrdersResult.Orders, 'Order'):
            self.log("Exito", "No hay datos que sincronizar")
            if not self.guarda_fechasincrotienda(self.esquema, self.codtienda):
                self.log("Error", "Fallo al guardar fecha última sincro")
                return self.small_sleep
            return False

        for order in response.ListOrdersResult.Orders.Order:

            idAmazon = qsatype.FLUtil.sqlSelect("az_ventasamazon", "idamazon", "idamazon = '{}'".format(order.AmazonOrderId))
            print(idAmazon)
            if not idAmazon:
                qsatype.FLSqlQuery().execSql("INSERT INTO az_ventasamazon (fechaalta, horaalta, lineassincronizadas, datoscabecera, idamazon, pedidoinformado, envioinformado) VALUES (CURRENT_DATE,CURRENT_TIME,false,'{}','{}', false, false)".format(etree.tostring(order).decode('utf-8'), order.AmazonOrderId))
                if not self.idamazon:
                    self.idamazon = order.AmazonOrderId
                else:
                    self.idamazon = ',' + order.AmazonOrderId

        return True

    def process_data(self, data):
        return True

    def sign_request(self, attr):
        string_to_sign = "POST\n{}\n/Orders/2013-09-01\n".format(self.driver.azHost) + attr

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
            self.log("Exito", "Las siguientes pedidos se han sincronizado correctamente: {}".format(self.idamazon))
        else:
            self.log("Exito", "No hay datos que sincronizar")

        return self.large_sleep

    def guarda_fechasincrotienda(self, esquema, codtienda):
        ahora = datetime.utcnow()
        hace_dos_hora = ahora - timedelta(hours=1)
        fecha = str(hace_dos_hora)[:10]
        hora = str(hace_dos_hora)[11:19]
        idsincro = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "id", "esquema = '{}' AND codtienda = '{}'".format(esquema, codtienda))

        if idsincro:
            qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE id = {}".format(fecha, hora, idsincro))
        else:
            qsatype.FLSqlQuery().execSql("INSERT INTO tpv_fechasincrotienda (codtienda, esquema, fechasincro, horasincro) VALUES ('{}', '{}', '{}', '{}')".format(codtienda, esquema, fecha, hora))

        return True
