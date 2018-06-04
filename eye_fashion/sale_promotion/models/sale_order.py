# -*- coding: utf-8 -*-
from dateutil import parser
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SalePromotion(models.Model):
    _inherit = 'sale.order'

    sale_promotion_id = fields.Many2one('sale.promotion', string="Sale Promotion")

    @api.multi
    def button_dump_sale_promotion(self):
        for order in self:
            if order.sale_promotion_id:
                sales_lines = []
                for line in order.order_line:
                    sales_lines.append(line)
                for line in order.order_line:
                    if line in sales_lines:
                        current_lines_indx = sales_lines.index(line)
                        for rule in order.sale_promotion_id.item_ids:
                            if rule.applied_on == 'product_category':
                                products = self.env['product.product']. search([('categ_id', '=', rule.categ_id.id)])
                                product_ids = []
                                for product in products:
                                    product_ids.append(product.id)
                                if line.product_id.id in product_ids and line.product_uom_qty == rule.min_quantity:
                                    del sales_lines[current_lines_indx]
                                    for s_line in sales_lines:
                                        s_line_indx = sales_lines.index(s_line)
                                        for gift_line in rule.promotion_rule_lines:
                                            if s_line.product_id.id == gift_line.product_id.id and s_line.product_uom_qty == gift_line.quantity:
                                                del sales_lines[s_line_indx]
                                                if line.price_unit > s_line.price_unit:
                                                    s_line.write({
                                                        'discount': 100,
                                                        'price_subtotal': 0,
                                                        })
                                                else:
                                                    line.write({
                                                        'discount': 100,
                                                        'price_subtotal': 0,
                                                        })
                                # elif line.product_id.id in product_ids and line.product_uom_qty < rule.min_quantity:
                                #     over_all_qty = line.product_uom_qty
                                #     s_line_indxs = []
                                #     for s_line in sales_lines:
                                #         if over_all_qty < rule.min_quantity:
                                #             if s_line.product_id.id in product_ids:
                                #                 over_all_qty += line.product_uom_qty
                            
                            elif rule.applied_on == 'product':
                                if line.product_id.id == rule.product_tmpl_id.id and line.product_uom_qty == rule.min_quantity:
                                    del sales_lines[current_lines_indx]
                                    for s_line in sales_lines:
                                        s_line_indx = sales_lines.index(s_line)
                                        for gift_line in rule.promotion_rule_lines:
                                            if s_line.product_id.id == gift_line.product_id.id and s_line.product_uom_qty == gift_line.quantity:
                                                del sales_lines[s_line_indx]
                                                if line.price_unit > s_line.price_unit:
                                                    s_line.write({
                                                        'discount': 100,
                                                        'price_subtotal': 0,
                                                        })
                                                else:
                                                    line.write({
                                                        'discount': 100,
                                                        'price_subtotal': 0,
                                                        })
                                # if line.product_id.id in product_ids and line.product_uom_qty < rule.min_quantity:
                                #     del sales_lines[current_lines_indx]
            else:
                raise UserError(_('Please Select an Promotion Rule.'))

            # if order.sale_promotion_id:
            #     date_order = parser.parse(order.date_order).strftime('%Y-%m-%d')
            #     product_list = []
            #     category_list = []
            #     for line in order.order_line:
            #         count = 0
            #         categ_count = 0
            #         if line.is_promotion_line:
            #             line.unlink()
            #         else:
            #             if product_list:
            #                 for data in product_list:
            #                     if data['product_id'] == line.product_id.id:
            #                         data['qty'] += line.product_uom_qty
            #                         count += 1
            #                 if count == 0:
            #                     product_list.append({
            #                         'product_id': line.product_id.id,
            #                         'qty': line.product_uom_qty,
            #                     })
            #             else:
            #                 product_list.append({
            #                     'product_id': line.product_id.id,
            #                     'qty': line.product_uom_qty,
            #                 })
            #             if category_list:
            #                 for prod in category_list:
            #                     if prod['category'] == line.product_id.categ_id.id:
            #                         prod['qty'] += line.product_uom_qty
            #                         categ_count += 1

            #                 if categ_count == 0:
            #                     category_list.append({
            #                         'qty': line.product_uom_qty,
            #                         'category': line.product_id.categ_id.id,
            #                     })
            #             else:
            #                 category_list.append({
            #                     'qty': line.product_uom_qty,
            #                     'category': line.product_id.categ_id.id,
            #                 })
            #     category_rule_ids = []
            #     product_rule_ids = []
            #     for obj in self.sale_promotion_id:
            #         for promo_lines in obj.item_ids:
            #             if not promo_lines.date_start or promo_lines.date_start <= date_order:
            #                 if not promo_lines.date_end or promo_lines.date_end >= date_order:
            #                     if promo_lines.applied_on == 'product_category':
            #                         categ_val = {'rule': promo_lines,
            #                                      'category': promo_lines.categ_id.id,
            #                                      'qty': promo_lines.min_quantity,
            #                                      }
            #                         category_rule_ids.append(categ_val)
            #                     elif promo_lines.applied_on == 'product':

            #                             pr_val = {'rule': promo_lines,
            #                                       'product_id': promo_lines.product_tmpl_id.id,
            #                                       'qty': promo_lines.min_quantity,
            #                                       }
            #                             product_rule_ids.append(pr_val)
            #     sale_line_obj = self.env['sale.order.line']
            #     if product_rule_ids and product_list:
            #         for data in product_list:
            #             rules = []
            #             for i in product_rule_ids:
            #                 if i['product_id'] == data['product_id']:
            #                     if data['qty'] >= i['rule'].min_quantity:
            #                         rules.append(i)
            #             if len(rules) > 1:
            #                 max_qty_rule = max(rules, key=lambda x: x['qty'])
            #                 for line in max_qty_rule['rule'].promotion_rule_lines:
            #                     sale_line_obj.create({
            #                         'name': line.product_id.name,
            #                         'price_unit': 0,
            #                         'product_uom_qty': line.quantity,
            #                         'order_id': order.id,
            #                         'discount': 0.0,
            #                         'product_uom': line.product_id.uom_id.id,
            #                         'product_id': line.product_id.id,
            #                         'tax_id': [],
            #                         'is_promotion_line': True,
            #                     })
            #             elif len(rules) == 1:
            #                 for r in rules:
            #                     for line in r['rule'].promotion_rule_lines:
            #                         sale_line_obj.create({
            #                             'name': line.product_id.name,
            #                             'price_unit': 0,
            #                             'product_uom_qty': line.quantity,
            #                             'order_id': order.id,
            #                             'discount': 0.0,
            #                             'product_uom': line.product_id.uom_id.id,
            #                             'product_id': line.product_id.id,
            #                             'tax_id': [],
            #                             'is_promotion_line': True,
            #                         })
            #             else:
            #                 pass

            #     if category_rule_ids and category_list:
            #         for categ in category_list:
            #             rules = []
            #             for r in category_rule_ids:
            #                 if categ['category'] == r['category']:
            #                     if categ['qty'] >= r['rule'].min_quantity:
            #                         rules.append(r)
            #             if len(rules) > 1:
            #                 max_qty_rule = max(rules, key=lambda x: x['qty'])
            #                 for line in max_qty_rule['rule'].promotion_rule_lines:
            #                     sale_line_obj.create({
            #                         'name': line.product_id.name,
            #                         'price_unit': 0,
            #                         'product_uom_qty': line.quantity,
            #                         'order_id': order.id,
            #                         'discount': 0.0,
            #                         'product_uom': line.product_id.uom_id.id,
            #                         'product_id': line.product_id.id,
            #                         'tax_id': [],
            #                         'is_promotion_line': True,
            #                     })
            #             elif len(rules) == 1:
            #                 for r in rules:
            #                     for line in r['rule'].promotion_rule_lines:
            #                         sale_line_obj.create({
            #                             'name': line.product_id.name,
            #                             'price_unit': 0,
            #                             'product_uom_qty': line.quantity,
            #                             'order_id': order.id,
            #                             'discount': 0.0,
            #                             'product_uom': line.product_id.uom_id.id,
            #                             'product_id': line.product_id.id,
            #                             'tax_id': [],
            #                             'is_promotion_line': True,
            #                         })
            #             else:
            #                 pass
            # else:
            #     raise UserError(_('Please Select an Promotion Rule.'))


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_promotion_line = fields.Boolean(string='Promotion Line')
