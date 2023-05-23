from odoo import models, fields


class InheritedResUser(models.Model):
    _inherit = "res.users"


    property_ids = fields.One2many(
        "estate.property",
        "seller_id",
        string="Sale properties",
        domain="[('available', '=', True)]"
    )
