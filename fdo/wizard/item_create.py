from openerp import api
from openerp.osv import fields, osv


class WizardItemCreate(osv.TransientModel):
    _name = "fdo.wizard_item_create"
    _description = "Temporary Item creation wizard"

    _columns = {
        "name": fields.char(
            string="Name",
            required=True
        ),
        "file": fields.binary(
            string="File",
            required=True
        ),
        "file_fname": fields.char(
            string="Filename",
            required=True
        )
    }

    @api.multi
    def action_create(self, args):
        for rec in self:
            item_id = rec.env["fdo.item"].create({
                "name": rec.name
            })

            attachment_id = rec.env["ir.attachment"].create({
                "name": rec.name,
                "datas_fname": rec.file_fname,
                "type": "binary",
                "datas": rec.file,
                "res_model": "fdo.item",
                "res_id": item_id.id
            })

            item_id.write({
                "attachment_id": attachment_id.id,
            })
