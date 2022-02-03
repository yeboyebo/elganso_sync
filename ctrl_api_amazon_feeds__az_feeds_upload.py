import hmac
import hashlib
import urllib.parse

from base64 import b64encode
from abc import ABC, abstractmethod
from collections import OrderedDict
from datetime import datetime, timedelta

from YBLEGACY import qsatype
from YBLEGACY.constantes import dict2xml, xml2dict

from controllers.base.default.controllers.upload_sync import UploadSync
from controllers.api.amazon.drivers.amazon import AmazonDriver
from controllers.api.amazon.feeds.serializers.feed_serializer import FeedSerializer


class AzFeedsUpload(UploadSync, ABC):

    referencias = []
    request_data = None

    def __init__(self, process_name, params=None):
        super().__init__(process_name, AmazonDriver(), params)

        self.small_sleep = 1200
        self.large_sleep = 1200
        self.no_sync_sleep = 1200

        self.referencias = []
        self.id_field = 'az.referencia'

        self.set_sync_params(self.get_param_sincro('amazon'))

    def get_data(self):
        data = self.get_db_data()
        if data == []:
            return data

        data = dict2xml(self.get_serializer().serialize(data), 'AmazonEnvelope')

        data = '<?xml version="1.0" encoding="utf-8"?>' + data
        data = self.replace_special_chars(data)
        self.request_data = bytes(data, 'iso-8859-1').decode('utf-8', 'ignore')

        return self.request_data

    def get_db_data(self):
        body = []

        q = self.get_query()
        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)

        for row in body:
            if row[self.id_field] not in self.referencias:
                self.referencias.append(row[self.id_field])

        return body

    def get_serializer(self):
        serializer = FeedSerializer()
        serializer.msg_type = self.get_msgtype()
        serializer.merchant_id = self.driver.azMerchant
        serializer.child_serializer = self.get_child_serializer()

        return serializer

    @abstractmethod
    def get_query(self):
        pass

    @abstractmethod
    def get_msgtype(self):
        pass

    @abstractmethod
    def get_feedtype(self):
        pass

    @abstractmethod
    def get_child_serializer(self):
        pass

    def send_data(self, data):
        attr = self.get_attributes(data)
        signature = self.sign_request(attr)
        url = "https://{}/?{}&Signature={}".format(self.driver.azHost, attr, signature)

        return self.driver.send_request("post", url=url, data=data)

    def after_sync(self, response_data=None):
        print(response_data)

        response = xml2dict(response_data)

        info = response.SubmitFeedResult.FeedSubmissionInfo

        if info.FeedProcessingStatus == '_SUBMITTED_':
            amazon_id = info.FeedSubmissionId

            qsatype.FLSqlQuery().execSql("INSERT INTO az_logamazon (idamazon, tipo, fecha, hora, procesadoaq, procesadoaz, peticion) VALUES ('{}', '{}', '{}', '{}', false, false, '{}')".format(amazon_id, self.get_msgtype(), str(datetime.now())[:10], str(datetime.now())[11:19], self.request_data))

            self.log("Exito", "Esquema '{}' sincronizado correctamente (referencias: {})".format(self.get_msgtype(), self.referencias))

            return amazon_id
        else:
            self.log("Error", "Esquema '{}' no se ha podido sincronizar correctamente (referencias: {})".format(self.get_msgtype(), self.referencias))

            return False

    def get_raw_attributes(self, data):
        return {
            "AWSAccessKeyId": self.driver.azAccessKey,
            "Action": "SubmitFeed",
            "Merchant": self.driver.azMerchant,
            "SignatureVersion": "2",
            "Timestamp": (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "Version": "2009-01-01",
            "ContentMD5Value": self.get_hash(data),
            "SignatureMethod": "HmacSHA256",
            "FeedType": self.get_feedtype(),
            "MarketplaceIdList.Id.1": self.driver.azMarketplaceId,
            "PurgeAndReplace": "false"
        }

    def get_attributes(self, data):
        attributes = self.get_raw_attributes(data)

        ordered_dict = OrderedDict(sorted(attributes.items()))
        return "&".join(["{}={}".format(key, self.url_encode(value)) for key, value in ordered_dict.items()])

    def get_hash(self, data):
        return b64encode(
            hashlib.md5(
                bytes(data, 'utf-8')
            ).digest()
        ).decode('utf-8')

    def url_encode(self, param):
        encoded = urllib.parse.quote(param)
        encoded = encoded.replace('/', '%2F')
        return encoded

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

    def replace_special_chars(self, data):
        data = data.replace("&", "&amp;")
        data = data.replace("€", "&euro;")
        data = data.replace("©", "&copy;")
        data = data.replace("®", " TM")

        data = data.replace("#", "&#35;")
        data = data.replace("Á", "&#193;")
        data = data.replace("É", "&#201;")
        data = data.replace("Í", "&#205;")
        data = data.replace("Ó", "&#211;")
        data = data.replace("Ú", "&#218;")
        data = data.replace("á", "&#225;")
        data = data.replace("é", "&#233;")
        data = data.replace("í", "&#237;")
        data = data.replace("ó", "&#243;")
        data = data.replace("ú", "&#250;")
        data = data.replace("Ñ", "&#209;")
        data = data.replace("ñ", "&#241;")
        data = data.replace("Ç", "&#199;")
        data = data.replace("ç", "&#231;")
        data = data.replace("Ü", "&#220;")
        data = data.replace("ü", "&#252;")
        data = data.replace("º", "&#176;")
        data = data.replace("@", "&#64;")
        data = data.replace("\r", "\n")
        data = data.replace("|", "&#124;")
        data = data.replace("!", "&#33;")
        data = data.replace("”", "&#34;")
        data = data.replace("“", "&#8220;")
        data = data.replace("$", "&#36;")
        data = data.replace("%", "&#37;")
        data = data.replace("’", "&#39;")
        data = data.replace("(", "&#40;")
        data = data.replace(")", "&#41;")

        data = data.replace("<br>", "\n")

        return data
