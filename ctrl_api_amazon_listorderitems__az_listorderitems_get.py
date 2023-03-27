import hmac
import hashlib
import urllib.parse
import time
from lxml import etree

from base64 import b64encode

from YBLEGACY import qsatype
from YBLEGACY.constantes import xml2dict

from datetime import datetime, timedelta
from abc import ABC
from collections import OrderedDict

from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.api.amazon.drivers.amazon import AmazonDriver


class AzListOrderItemsResultGet(DownloadSync, ABC):

    idamazon = None

    def __init__(self, params=None):
        super().__init__("azlistorderitemsget", AmazonDriver(), params)

        self.set_sync_params(self.get_param_sincro('amazon'))

    def get_data(self):
        idAmazon = qsatype.FLUtil.sqlSelect("az_ventasamazon", "idamazon", "lineassincronizadas = FALSE LIMIT 1")
        if not idAmazon:
            return []

        attr = self.get_attributes(idAmazon)
        signature = self.sign_request(attr)
        url = "https://{}/Orders/2013-09-01?{}&Signature={}".format(self.driver.azHost, attr, signature)
        return self.driver.send_request("post", url=url)

    def get_attributes(self, idamazon):
        attributes = self.get_raw_attributes(idamazon)

        ordered_dict = OrderedDict(sorted(attributes.items()))
        return "&".join(["{}={}".format(key, self.url_encode(value)) for key, value in ordered_dict.items()])

    def get_raw_attributes(self, idamazon):
        return {
            "Action": "ListOrderItems",
            "SellerId": self.driver.azMerchant,
            "SignatureVersion": "2",
            "AWSAccessKeyId": self.driver.azAccessKey,
            "Timestamp": (datetime.now() + timedelta(hours=-2)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "Version": "2013-09-01",
            "SignatureMethod": "HmacSHA256",
            "AmazonOrderId": idamazon
        }

    def process_all_data(self, all_data):
        if all_data == []:
            self.log("Exito", "No hay datos que sincronizar")
            return False

        response = xml2dict(bytes(all_data, 'utf-8'))
        if not hasattr(response.ListOrderItemsResult, 'AmazonOrderId'):
            self.log("Exito", "No hay datos que sincronizar")
            return False

        idAmazon = response.ListOrderItemsResult.AmazonOrderId

        for orderItem in response.ListOrderItemsResult.OrderItems:
            qsatype.FLSqlQuery().execSql("UPDATE az_ventasamazon SET lineassincronizadas = TRUE, datoslineas = '{}' WHERE idamazon = '{}'".format(etree.tostring(orderItem).decode('utf-8'), idAmazon))
            self.idamazon = idAmazon

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
        if self.idamazon:
            self.log("Exito", "Las siguientes pedidos se han sincronizado correctamente: {}".format(self.idamazon))
            return self.small_sleep
        else:
            self.log("Exito", "No hay datos que sincronizar")

        return self.large_sleep
