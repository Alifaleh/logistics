# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError



def test(var):
    test_file = open("/usr/lib/python3/dist-packages/odoo/c-addons/test_file.txt","a")
    test_file.write(var)
    test_file.close()




class LogisticsShipment(models.Model):
    _name = 'logistics.shipment'
    _description = 'logistics.shipment'
    _rec_name = "name_seq"

    _status = [('draft', 'draft'), ('in_progress', 'In Progress'), ('accepted', 'Accepted'), ('canceled', 'Canceled')]

    name_seq = fields.Char(string="id", required = True, copy=False, readonly=True, index=True, default=lambda self: self.env['ir.sequence'].next_by_code('logistics.shipment.code'))
    status = fields.Selection(_status, default='draft')
    contract_id = fields.Many2one('contract.contract',string='Contract')
    origin_ids = fields.Many2many('purchase.order', string="Origin",relation="shipment_purchase",column1="col1",column2="col2")
    origin_is_selected = fields.Boolean(default=False)
    customer = fields.Many2one('res.partner',string='Partner')
    vendor = fields.Char()
    multi_vendor = fields.Boolean(string="Multi-Vendor")
    tags_ids = fields.Many2many('logistics.shipment.tags',string="Tags")
    shipment_total = fields.Float(compute="_compute_shipment_total",string='Shipment Total')
    shipment_lines = fields.One2many('logistics.shipment.line', 'shipment_id', string='Shipment Products')

    purchase_orders = fields.One2many('logistics.shipment.pos', 'shipment_id', string="Purchase Orders")



    def _compute_shipment_total(self):
        shipment_total=0
        for line in self.shipment_lines:
            shipment_total+=line.amount_total
        self.shipment_total=shipment_total



    @api.onchange('origin_ids')
    def show_get_pos_button(self):
        if(self.origin_ids):
            self.origin_is_selected=True
        else:
            self.origin_is_selected=False

    def get_from_pos(self):
        for po in self.origin_ids:
            for line in po.order_line:
                self.shipment_lines.create({"shipment_id":self.id,'product_id':line.product_id.id,'qty':line.product_qty, "unit_price":line.price_unit,"amount_total":line.price_unit*line.product_qty})

                    

class LogisticsShipmentLine(models.Model):

    _name = 'logistics.shipment.line'
    _description = 'logistics.shipment.line'

    shipment_id = fields.Many2one('logistics.shipment',string='Shipment ID')
    product_id = fields.Many2one('product.product', string="Product")
    vendors = fields.Char()
    qty = fields.Integer()
    unit_price = fields.Float()
    amount_total = fields.Float()


class LogisticsShipmentTags(models.Model):

    _name = 'logistics.shipment.tags'
    _description = 'logistics.shipment.tags'
    _rec_name="name"

    name = fields.Char(string='Tag')
    color = fields.Integer()



class LogisticsShipmentPurchaseOrders(models.Model):
    _name = 'logistics.shipment.pos'
    _description = 'logistics.shipment.pos'

    shipment_id = fields.Many2one('logistics.shipment')

    purchase_orders_ids = fields.Many2one('purchase.order',string='Purchase Order')
    type_id = fields.Many2one('logistics.shipment.transtypes', string='type')
    is_transport = fields.Boolean(string="Is Transport", related="type_id.is_transport")
    from_id = fields.Many2one('res.country.state')
    to_id = fields.Many2one('res.country.state')
    amount = fields.Float(string="Total Amount")

    @api.onchange("purchase_orders_ids")
    def get_po_total_amount(self):
        self.amount = self.purchase_orders_ids.amount_total



class LogisticsShipmentTransTypes(models.Model):
    _name = 'logistics.shipment.transtypes'
    _description = 'logistics.shipment.transtypes'
    _rec_name = "name"

    name = fields.Char(string="Name")    
    is_transport = fields.Boolean(string="Is Transport")



class PurchaseOrderExpence(models.Model):
    _inherit="purchase.order"
    is_shipment_expence = fields.Boolean(string="Is Shipment Expense", default=False)