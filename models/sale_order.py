from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends(
        "order_line.x_total",
        "order_line.price_tax",
        "order_line.price_total",
        "order_line.price_subtotal",
    )
    def _compute_amounts(self):
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            amount_untaxed = sum(lines.mapped("x_total"))
            amount_tax = sum(lines.mapped("price_tax"))
            order.update(
                {
                    "amount_untaxed": order.currency_id.round(amount_untaxed),
                    "amount_tax": order.currency_id.round(amount_tax),
                    "amount_total": order.currency_id.round(amount_untaxed + amount_tax),
                }
            )
