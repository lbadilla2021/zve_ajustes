from odoo import api, models
from odoo.tools import format_amount


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

    @api.depends_context("lang")
    @api.depends(
        "order_line.tax_id",
        "order_line.price_unit",
        "amount_total",
        "amount_untaxed",
        "currency_id",
        "order_line.x_total_flete",
    )
    def _compute_tax_totals(self):
        super()._compute_tax_totals()
        for order in self:
            if not order.tax_totals:
                continue

            untaxed = order.currency_id.round(
                sum(order.order_line.filtered(lambda l: not l.display_type).mapped("x_total"))
            )
            amount_tax = order.currency_id.round(order.tax_totals.get("amount_tax", order.amount_tax))
            amount_total = order.currency_id.round(untaxed + amount_tax)

            order.tax_totals["amount_untaxed"] = untaxed
            order.tax_totals["amount_total"] = amount_total
            order.tax_totals["formatted_amount_untaxed"] = format_amount(
                self.env, untaxed, currency=order.currency_id
            )
            order.tax_totals["formatted_amount_total"] = format_amount(
                self.env, amount_total, currency=order.currency_id
            )

            for subtotal in order.tax_totals.get("subtotals", []):
                if subtotal.get("name") in ("Untaxed Amount", "Neto", "Subtotal"):
                    subtotal["amount"] = untaxed
                    subtotal["formatted_amount"] = format_amount(
                        self.env, untaxed, currency=order.currency_id
                    )
                    break
