import base64

from openerp.osv import fields, osv


class Session(osv.Model):
    _name = "fdo.session"
    _description = "Session for FDO Tool"
    _rec_name = "token"

    def _compute_link(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context=context):
            res[rec.id] = self._get_link(rec.token)

        return res

    _columns = {
        "token": fields.char(
            string="Token",
            help="Ont-Time token for tool integration",
            required=True
        ),
        "user_id": fields.many2one(
            string="Related user",
            obj="res.users",
            required=True
        ),
        "link": fields.function(
            string="Link",
            fnct=_compute_link,
            type="char"
        )
    }

    @staticmethod
    def _get_link(token=""):
        url = "http://127.0.0.1:8069|%s" % token
        return "odoo://do?action=%s" % base64.b64encode(url)
