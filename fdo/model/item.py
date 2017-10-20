from openerp.osv import fields, osv


class Item(osv.Model):
    _name = "fdo.item"
    _description = "Temporary Item for development"

    _columns = {
        "name": fields.char(
            string="Name",
            required=True
        ),
        "attachment_id": fields.many2one(
            string="File",
            obj="ir.attachment"
        )
    }
