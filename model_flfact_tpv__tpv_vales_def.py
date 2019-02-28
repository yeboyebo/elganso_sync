
# @class_declaration elganso_sync #
class elganso_sync(flfact_tpv):

    def elganso_sync_consultavale(self, params):
        try:
            if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
                if "codvaleweb" not in params:
                    return {"Error": "Formato Incorrecto", "status": 0}
                codvaleweb = params['codvaleweb']
                q = qsatype.FLSqlQuery()
                q.setTablesList(u"tpv_vales")
                q.setSelect(u"saldoconsumido, codigo, total, codvaleweb, saldopendiente, coddivisa")
                q.setFrom(u"tpv_vales")
                q.setWhere(ustr(u"codvaleweb = '", codvaleweb, u"'"))
                if not q.exec_():
                    return {"Error": "Vale incorrecto", "status": -1}
                if q.size() > 1:
                    return {"Error": "Vale asociado a mas de una devolucion", "status": -2}
                if not q.next():
                    return {"Error": "Vale incorrecto", "status": -3}

                saldoconsumido = q.value("saldoconsumido")
                codigo = q.value("codigo")
                total = q.value("total")
                codvaleweb = q.value("codvaleweb")
                saldopendiente = q.value("saldopendiente")
                coddivisa = q.value("coddivisa")
                if saldopendiente == 0:
                    return {"saldoconsumido": saldoconsumido, "codigo": codigo, "total": total, "codvaleweb": codvaleweb, "saldopendiente": saldopendiente, "coddivisa": coddivisa}
                if not saldopendiente or saldopendiente < 0:
                    return {"Error": "Vale incorrecto", "status": 1}
                return {"saldoconsumido": saldoconsumido, "codigo": codigo, "total": total, "codvaleweb": codvaleweb, "saldopendiente": saldopendiente, "coddivisa": coddivisa}
            else:
                return {"Error": "Petición Incorrecta", "status": -1}
        except Exception as e:
            qsatype.debug(ustr(u"Error inesperado consulta de vale: ", e))
            return {"Error": "Petición Incorrecta", "status": -2}
        return False

    def elganso_sync_actualizavale(self, params):
        try:
            if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
                if "refvale" not in params or "idsincropago" not in params or "total" not in params:
                    return {"Error": "Formato Incorrecto", "status": -1}
                refvale = params['refvale']
                codigo = refvale
                idsincropago = params['idsincropago']
                total = params['total']
                curVale = qsatype.FLSqlCursor(u"tpv_vales")
                curVale.setModeAccess(curVale.Edit)
                curVale.refreshBuffer()
                curVale.select(ustr(u"codigo = '", codigo, u"'"))

                # Comprobaciones
                if not curVale.first():
                    qsatype.debug(ustr(u"El vale no esta activo o no se encuentra: ", codigo))
                    return {"Error": "El vale no se encuentra", "status": -1}
                # if (float(curVale.valueBuffer("saldopendiente")) - (float(total)) * -1) <= 0:
                #     importe = float(curVale.valueBuffer("saldopendiente")) * -1

                # Insertamos movibono
                if not qsatype.FLUtil.sqlInsert(u"tpv_movivale", [u"total", u"idsincropago", u"refvale"], [total, idsincropago, curVale.valueBuffer("referencia")]):
                    return {"Error": "Error en insercion de movimiento de bono", "status": -4}

                saldoconsumido = qsatype.FLUtil.sqlSelect(u"tpv_movivale", u"SUM(total)", ustr(u"refvale = '", curVale.valueBuffer("referencia"), u"'"))
                curVale.setValueBuffer("saldoconsumido", saldoconsumido)
                saldopendiente = curVale.valueBuffer("total") - saldoconsumido
                curVale.setValueBuffer("saldopendiente", saldopendiente)
                curVale.setValueBuffer("fechamod", str(qsatype.Date())[:10])
                curVale.setValueBuffer("horamod", str(qsatype.Date())[11:])
                if not curVale.commitBuffer():
                    return {"Error": "Error actualizando bono", "status": -6}
                return {"saldoPendiente": saldopendiente, "status": 1}
            else:
                return {"Error": "Petición Incorrecta", "status": 0}
        except Exception as e:
            qsatype.debug(params)
            qsatype.debug(ustr(u"Error inesperado generacion de movimiento de vale: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def __init__(self, context=None):
        super().__init__(context)

    def consultavale(self, params):
        return self.ctx.elganso_sync_consultavale(params)

    def actualizavale(self, params):
        return self.ctx.elganso_sync_actualizavale(params)

