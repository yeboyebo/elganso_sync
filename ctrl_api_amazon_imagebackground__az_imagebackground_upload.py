import requests
from os import path
from abc import ABC
from YBLEGACY import qsatype

from controllers.api.amazon.drivers.apibg_driver import ApiBgDriver
from controllers.base.default.controllers.upload_sync import UploadSync
from controllers.api.amazon.imagebackground.serializers.imagebackground_serializer import ImageBackgroundSerializer


class AzImageBackgroundUpload(UploadSync, ABC):

    def __init__(self, params=None):
        super().__init__("azimagebackgroundupload", ApiBgDriver(), params)

        self.set_sync_params(self.get_param_sincro('apibackgroundimage'))

    def get_data(self):
        data = self.get_db_data()
        if data == []:
            return data

        body = []
        for d in data:
            body.append(self.get_serializer().serialize(d))

        return body

    def get_db_data(self):
        body = []

        q = self.get_query()
        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        data = []
        for row in body:
            urls = row['urls.urls'].split(',')

            for url in urls:
                splitted = url.split('/')
                data.append({'referencia': row['az.referencia'], 'name': splitted[-1], 'url': url})

        return data

    def get_query(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("az.referencia, urls.urls")
        q.setFrom("az_articulosamazon az INNER JOIN eg_urlsimagenesarticulosmgt urls ON az.referencia = urls.referencia")
        q.setWhere("az.articulocreado AND NOT az.sincroimagenes AND NOT az.errorsincro AND urls.urls IS NOT NULL AND urls.urls <> '' AND (urls.urls_sinfondo IS NULL OR urls.urls_sinfondo = '') LIMIT 1")

        return q

    def send_data(self, data):
        referencia = data[0]['referencia']

        for d in data:
            print(d['serialized'])
            image_path = '{}{}'.format(self.driver.apiBgImagePath, d['name'])

            if not path.isfile(image_path):
                response = requests.post(
                    self.driver.apiBgImageUrl,
                    data=d['serialized'],
                    headers={'X-Api-Key': self.driver.apiBgImageKey}
                )
                if response.status_code == requests.codes.ok:
                    with open(image_path, 'wb') as out:
                        out.write(response.content)
                else:
                    self.log("Error", "Esquema '{}' - Referencia: '{}' - Imagen: '{}' ({})".format(self.get_msgtype(), referencia, d['name'], response.text))
                    continue

            d['new_url'] = '{}{}'.format(self.driver.apiBgImageNewUrl, d['name'])

        return data

    def after_sync(self, response_data=None):
        print(response_data)

        referencia = response_data[0]['referencia']
        new_urls = []

        for data in response_data:
            if 'new_url' in data:
                new_urls.append(data['new_url'])

        new_urls = ','.join(new_urls)

        if new_urls == '':
            qsatype.FLSqlQuery().execSql("UPDATE az_articulosamazon SET errorsincro = true, descerror = 'No se pudo limpiar ninguna imagen para el artículo' WHERE referencia = '{}'".format(referencia))
            raise NameError("Esquema: '{}' - Referencia: '{}' (No se pudo limpiar ninguna imagen para el artículo)".format(self.get_msgtype(), referencia))

        qsatype.FLSqlQuery().execSql("UPDATE eg_urlsimagenesarticulosmgt SET urls_sinfondo = '{}' WHERE referencia = '{}'".format(new_urls, referencia))

        self.log("Éxito", "Esquema '{}' sincronizado correctamente (referencias: {})".format(self.get_msgtype(), referencia))

        return self.small_sleep

    def get_serializer(self):
        return ImageBackgroundSerializer()

    def get_msgtype(self):
        return 'ImageBackground'
