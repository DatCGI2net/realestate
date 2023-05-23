from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class EstatePropertyModel(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _order = "id desc"

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
    orientation_north = 'north'
    orientation_south = 'south'
    orientation_east = 'east'
    orientation_west = 'west'

    garden_orientation = fields.Selection(
        selection=[
            (orientation_north, 'North'),
            (orientation_south, 'South'),
            (orientation_east, 'East'),
            (orientation_west, 'West'),
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

    available = fields.Boolean(
        compute='_is_available',
        store=True, readonly=True
    )

    property_type_id = fields.Many2one(
        "estate.property.type",
        string="Property Type"
    )
    seller_id = fields.Many2one(
        "res.users",
        string="Seller",
        default=lambda self: self.env.uid,
    )
    buyer_id = fields.Many2one(
        "res.partner",
        string="Buyer",
        copy=False,
    )

    tag_ids = fields.Many2many(
        "estate.property.tag",
        string="Property Tag",
    )

    offer_ids = fields.One2many("estate.property.offer",
                               "property_id",
                                string="Offers",
                                copy=False)

    total_area = fields.Integer(
        compute='_get_total_area',

    )
    best_price = fields.Float(
        compute='_get_best_price',
        copy=False,
        store=True,
    )

    @api.depends('offer_ids')
    def _get_best_price(self):
        for record in self:
            if record.offer_ids and len(record.offer_ids):
                record.best_price = max(record.offer_ids.mapped('price'))


    @api.depends('garden_area', 'living_area')
    def _get_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area


    @api.depends('date_availability')
    def _is_available(self):
        today = fields.Date.today()
        for record in self:
            record.available = record.date_availability and record.date_availability >= today

    @api.onchange('garden')
    def _update_garden_orientation(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = self.orientation_north
        else:
            self.garden_area = None
            self.garden_orientation = None

    sold_or_cancelled_states = [state_sold, state_cancelled]
    def action_sold(self):

        if self.state in self.sold_or_cancelled_states:
            raise UserError(_('This property was sold already!'))


        self.write({'state': self.state_sold})
        return True

    def action_cancel(self):

        if self.state in self.sold_or_cancelled_states:
            raise UserError(_('This property was cancelled already!'))

        self.write({'state':self.state_cancelled})

        return  True

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'The expected price must be positive.'),
        ('check_selling_price', 'CHECK(selling_price > 0)', 'The selling price must be positive.'),
        ('check_unique_name', 'UNIQUE(name)', 'The property already in-use'),
    ]

    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if float_compare(
                    record.selling_price, record.expected_price * 0.9,
                    precision_digits=2) == -1:
                raise ValidationError("Offered price is too low")

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_cancelled(self):

        for record in self:
            if record.state not in [self.state_new, self.state_cancelled]:
                raise UserError("Record cannot be deleted")
        for record in self:
            [offer.unlink() for offer in record.offer_ids]


class EstatePropertyTypeModel(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _order = "name"

    name = fields.Char(required=True)
    property_ids = fields.One2many(
        "estate.property",
        "property_type_id",
        string="Properties"
    )
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")


    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_type_id",
    )
    offer_count = fields.Integer(
        compute='_get_offer_count',
    )

    @api.depends('offer_ids')
    def _get_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    def action_offer_count(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Offer',
            'view_mode': 'tree',
            'res_model': 'estate.property.offer',
            'domain': [('property_type_id', '=', self.id)],
            'context': "{'create': False}"
        }



class EstatePropertyTagModel(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [
        ('check_unique_name', 'UNIQUE(name)', 'The tag already in-use'),
    ]

class EstatePropertyOfferModel(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    offer_accepted = 'Accepted'
    offer_refused = 'Refused'
    offer_statuses = [
        (offer_accepted, offer_accepted),
        (offer_refused, offer_refused)
    ]
    price = fields.Float()
    status = fields.Selection(
        selection=offer_statuses,
        copy=False,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Parter",
        required=True,
    )
    property_id = fields.Many2one(
        "estate.property",
        string="Property",
        required=True,
    )
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(default=lambda self: fields.Date.today() + timedelta(days=7))

    property_type_id = fields.Many2one(
        related="property_id.property_type_id",
        store=True)

    def action_confirm(self):
        self.property_id.buyer_id = self.partner_id
        self.property_id.selling_price = self.price
        self.property_id.state = self.property_id.state_offer_accepted
        self.write({
            'status': self.offer_accepted,
            'property_id': self.property_id
        })
        return True
    def action_cancel(self):
        self.write({
            'status': self.offer_refused})
        return True

    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'The price must be positive.'),

    ]

    @api.model
    def create(self, vals):
        property_id = vals.get('property_id', 0)
        price = vals.get('price', 0)
        property = self.env['estate.property'].browse(property_id)
        offers = property.offer_ids.search([
            ('property_id', '=', property_id),
            ('price', '>', price)])
        if len(offers):
            raise UserError(_("Price too low"))

        property.write({'state': EstatePropertyModel.state_offer_received})

        result =  super(EstatePropertyOfferModel, self).create(vals)

        return result

