from odoo import models, fields
from datetime import timedelta
class TestModel(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(readonly=True, default=lambda self: fields.Date.today() + timedelta(days=90))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ]
    )
    active = fields.Boolean()
    state_new = 'New'
    state_offer_received = 'Offer Received'
    state_offer_accepted = 'Offer Accepted'
    state_sold = 'Sold'
    state_cancelled = 'Cancelled'


    state = fields.Selection(
        default=state_new,
        selection=[
            (state_new, state_new),
            (state_offer_received, state_offer_received),
            (state_offer_accepted, state_offer_accepted),
            (state_sold, state_sold),
            (state_cancelled, state_cancelled),
        ]
    )



