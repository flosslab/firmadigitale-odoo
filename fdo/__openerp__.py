{
    "name": "Firma Digitale Odoo",
    "version": "8.0.0.0.0",
    "category": "Document",
    "summary": "Document Digital Sign",
    "description": """
Firma Digitale Odoo
================================================

This module adds the digital sign feature to ir_attachments
    """,
    "author": "Flosslab",
    "website": "http://www.flosslab.com",
    "depends": [
        "base",
    ],
    "data": [
        "menu/action.xml",
        "menu/root.xml",
        "menu/tool.xml",
        "menu/development.xml",
        "view/session.xml",
        "view/job.xml",
        "view/item.xml",
        "view/ir_attachment.xml",
        "wizard/item_create.xml"
    ],
    "installable": True
}
