from YBLEGACY import qsatype
import json
from controllers.base.magento2.price.controllers.price_upload import PriceUpload
from controllers.api.magento2.price.serializers.price_serializer import PriceSerializer

class Mg2PriceUpload(PriceUpload):

    error = False
    _idls = None

    def __init__(self, params=None):
        super().__init__("mg2price", params)

        price_params = self.get_param_sincro('mg2PricesUpload')
        self.price_url = price_params['url']
        self.price_test_url = price_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))
        
        self.small_sleep = 1

    def get_data(self):
        datos = self.insert_datos_sincro()
        data = self.get_db_data()

        if data == []:
            return data

        new_price = []
        idObjeto = None
        for idx in range(len(data)):
            price = self.get_price_serializer().serialize(data[idx])
            new_price.append(price)
            if not idObjeto:
                idObjeto = str(data[idx]["ls.id"])
                self._idls = str(data[idx]["ls.id"])

            if str(data[idx]["ls.id"]) != idObjeto:
                idObjeto = str(data[idx]["ls.id"])
                self._idls += "," + str(data[idx]["ls.id"])

        if not new_price:
            return False

        return {
            "prices": new_price
        }

    def send_data(self, data):
        price_url = self.price_url if self.driver.in_production else self.price_test_url

        for idx in range(len(data["prices"])):
            del data["prices"][idx]["children"]

        if data:
            try:
                print("DATA: ", json.dumps(data))
                print("URL: ", price_url)
                self.send_request("post", url=price_url, data=json.dumps(data))
            except Exception as e:
                print("exception")
                # print(json.dumps(e))
                self.error = True

        return data

    def insert_datos_sincro(self):

        fechasincro = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "fechasincro", "codtienda = 'AWEB' AND esquema = 'PRICES_WEB'")
        horasincro = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "LEFT(CAST(horasincro AS TEXT), 8)", "codtienda = 'AWEB' AND esquema = 'PRICES_WEB'")

        if not fechasincro or fechasincro is None:
            fechasincro = "2021-10-01"
        else:
            fechasincro = str(fechasincro)[:10]

        if not horasincro or horasincro is None:
            horasincro = "00:00:00"
        else:
            horasincro = str(horasincro)[-(8):]

        filtro_fechas_alta = "(a.fechaalta > '{}' OR (a.fechaalta = '{}' AND a.horaalta >= '{}'))".format(fechasincro, fechasincro, horasincro)
        filtro_fechas_mod = "(a.fechamod > '{}' OR (a.fechamod = '{}' AND a.horamod >= '{}'))".format(fechasincro, fechasincro, horasincro)
        
        qsatype.FLSqlQuery().execSql("INSERT INTO lineassincro_catalogo (idobjeto, descripcion, tiposincro, website, sincronizado)(select at.referencia || '-' || at.talla || '-' || a.pvp || '-' || st.idmagento, 'sincro tarifa ' || at.referencia || '-' || at.talla || '-' || a.pvp || '-' || st.idmagento, 'sincrotarifas', 'MG2', false from articulostarifas a inner join mg_storeviews st on a.codtarifa = st.codtarifa inner join atributosarticulos at ON a.referencia = at.referencia inner join lineassincro_catalogo l on a.referencia = l.idobjeto WHERE a.pvp > 0 and l.tiposincro = 'Enviar productos' and l.website = 'MG2' AND a.sincronizado = FALSE AND l.sincronizado = TRUE AND ({} OR {}) GROUP BY at.referencia, at.talla, a.pvp, st.idmagento ORDER BY at.referencia, st.idmagento, at.talla)".format(filtro_fechas_alta, filtro_fechas_mod));
         
        return True

    def get_db_data(self):
        body = []
        
        q = qsatype.FLSqlQuery()
        q.setSelect("ls.id, ls.idobjeto")
        q.setFrom("lineassincro_catalogo ls")
        q.setWhere("ls.website = 'MG2' and ls.tiposincro = 'sincrotarifas' and ls.sincronizado = false ORDER BY ls.id LIMIT 20")
        
        q.exec_()

        body = []
        if not q.size():
            return body

        body = self.fetch_query(q)
        self.error = False

        return body

    def get_price_serializer(self):
        return PriceSerializer()

    def after_sync(self, response_data=None):
        print("SSW: ", self._idls)
        if self.error:
            self.log("Error", "No se pudo sincronizar las tarifas de articulos: {})".format(self._idls))
            return self.small_sleep

        qsatype.FLSqlQuery().execSql("UPDATE articulostarifas SET sincronizado = TRUE WHERE sincronizado = FALSE AND ((fechamod < '{}' OR (fechamod = '{}' AND horamod <= '{}')) OR (fechaalta < '{}' OR (fechaalta = '{}' AND horaalta <= '{}')))".format(self.start_date, self.start_date, self.start_time, self.start_date, self.start_date, self.start_time))
        qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE codtienda = 'AWEB' AND esquema = 'PRICES_WEB'".format(self.start_date, self.start_time))
        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE id IN ({})".format(self._idls))

        self.log("Exito", "Tarifas de precio sincronizadas correctamente {}".format(self._idls))

        return self.small_sleep
