from openerp import api
from openerp.osv import fields, osv


class IrAttachment(osv.Model):
    _inherit = "ir.attachment"

    _columns = {
        "signed_attachment_id": fields.one2many(
            string="Related Signed Attachment",
            obj="ir.attachment",
            fields_id="original_attachment_id"
        ),
        "original_attachment_id": fields.many2one(
            string="Source Attachment for signature",
            obj="ir.attachment"
        )
    }

    @api.multi
    def action_sign(self):
        self.ensure_one()

        session_id = self.env["fdo.session"].generate_session(self._uid)
        job_id = self.env["fdo.job"].generate_sign_job(session_id=session_id, attachmentid=self.ids[0])

        return {
            "type": "ir.actions.act_url",
            "url": "/fdo/sign/single/%d" % session_id.id,
            "target": "self",
        }
