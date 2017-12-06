from openerp.osv import fields, osv
from openerp.tools.translate import _


class Job(osv.Model):
    _name = "fdo.job"
    _description = "Jobs in Session for FDO Tool"

    ACTIONS_SIGN = ("sign", _("Sign file"))

    ACTIONS = [
        ACTIONS_SIGN
    ]

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
        ),
        "status": fields.selection(
            selection=STATUS,
            string="Status",
            required=True
        )
    }

    _defaults = {
        "status": STATUS_PREPARED[0]
    }

    def generate_sign_job(self, session_id, attachmentid):
        return self.create({
            "session_id": session_id.id,
            "processed": False,
            "action": self.ACTIONS_SIGN[0],
            "attachment_id": attachmentid,
        })
