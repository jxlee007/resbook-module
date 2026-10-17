from odoo import models, fields

class ResourceBookingSlot(models.Model):
    _name = 'resource.booking.slot'
    _description = 'Resource Booking Slot'

    start_datetime = fields.Datetime(string='Start Time', required=True)
    end_datetime = fields.Datetime(string='End Time', required=True)
    state = fields.Selection([
        ('available', 'Available'),
        ('booked', 'Booked'),
    ], string='Slot Status', default='available', required=True)