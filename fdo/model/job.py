from openerp.osv import fields, osv
from openerp.tools.translate import _


class Job(osv.Model):
    _name = "fdo.job"
    _description = "Jobs in Session for FDO Tool"

    ACTIONS = [
        ("sign", _("Sign file"))
    ]

    _columns = {
        "session_id": fields.many2one(
            string="Session",
            obj="fdo.session",
            required=True
        ),
        "action": fields.selection(
            selection=ACTIONS,
            string="Action",
            required=True
        ),
        "attachment_id": fields.many2one(
            string="Source File",
            obj="ir.attachment",
            required=True
        )
    }
