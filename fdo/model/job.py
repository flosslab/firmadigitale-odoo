from openerp.osv import fields, osv
from openerp.tools.translate import _


class Job(osv.Model):
    _name = "fdo.job"
    _description = "Jobs in Session for FDO Tool"

    ACTIONS = [
        ("sign", _("Sign file"))
    ]

    def _compute_name(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context=context):
            res[rec.id] = "%s - %s - %s" % (rec.session_id, rec.action, rec.attachment_id)

        return res

    _columns = {
        "name": fields.function(
            string="Link",
            fnct=_compute_name,
            type="char"
        ),
        "session_id": fields.many2one(
            string="Session",
            obj="fdo.session",
            required=True
        ),
        "processed": fields.boolean(
            string="Processed",
            required=True,
            default=False
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
