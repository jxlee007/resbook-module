from odoo import models, fields

class ResourceBooking(models.Model):
    _name = 'resource.booking'
    _description = 'Resource Booking'

    name = fields.Char(string='Resource Name', required=True)