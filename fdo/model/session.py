import base64
import random
import string

from openerp.osv import fields, osv
from openerp.tools.translate import _


class Session(osv.Model):
    _name = "fdo.session"
    _description = "Session for FDO Tool"
    _rec_name = "token"

    STATUS_PREPARED = ("prepared", _("Prepared"))
    STATUS_WORKING = ("working", _("Working"))
    STATUS_COMPLETED = ("completed", _("Completed"))
    STATUS_ERROR = ("error", _("Error"))

    STATUS = [
        STATUS_PREPARED,
        STATUS_WORKING,
        STATUS_COMPLETED,
        STATUS_ERROR
    ]

    def _compute_link(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context=context):
            url_prefix = rec.env["ir.config_parameter"].get_param("web.base.url", "")
            res[rec.id] = self._get_link(url_prefix, rec.token)

        return res

    _columns = {
        "token": fields.char(
            string="Token",
            help="Ont-Time token for tool integration",
            unique=True,
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
        ),
        "status": fields.selection(
            selection=STATUS,
            string="Status",
            required=True
        ),
        "last_contact": fields.datetime(
            string="Last Contact",
            required=False
        )
    }

    _defaults = {
        "status": STATUS_PREPARED[0]
    }

    def generate_session(self, userid):
        return self.create({
            "token": self._generate_token(),
            "user_id": userid
        })

    @staticmethod
    def _get_link(url_prefix="", token=""):
        url = "%s|%s" % (url_prefix, token)
        return "odoo://do?action=%s" % base64.b64encode(url)

    @staticmethod
    def _generate_token():
        return "".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(16))
