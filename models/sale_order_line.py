from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    x_posicion = fields.Integer(string="Posición")
    x_recinto = fields.Char(string="Recinto", size=80)
    x_garantia_id = fields.Many2one("sale.dimension.warranty", string="Garantía")

    x_espesor = fields.Integer(string="Espesor")
    x_ancho = fields.Integer(string="Ancho")
    x_alto = fields.Integer(string="Alto")

    x_valor_flete_unitario = fields.Integer(string="Valor Flete Un.")
    x_total_flete = fields.Integer(
        string="Total Flete",
        compute="_compute_total_flete",
        store=True,
    )
    x_total = fields.Monetary(
        string="Total",
        currency_field="currency_id",
        compute="_compute_x_total",
        store=True,
    )

    @api.depends("x_valor_flete_unitario", "product_uom_qty")
    def _compute_total_flete(self):
        for rec in self:
            rec.x_total_flete = int((rec.x_valor_flete_unitario or 0) * (rec.product_uom_qty or 0))

    @api.depends("price_subtotal", "x_total_flete")
    def _compute_x_total(self):
        for rec in self:
            rec.x_total = (rec.price_subtotal or 0.0) + (rec.x_total_flete or 0)

    @api.constrains("x_espesor", "x_ancho", "x_alto")
    def _check_dimension_rules(self):
        Thickness = self.env["sale.dimension.thickness"]
        Range = self.env["sale.dimension.range"]

        active_range = Range.search([("active", "=", True)], limit=1)

        for rec in self:
            if rec.x_espesor not in (False, None):
                allowed = Thickness.search_count(
                    [("active", "=", True), ("value", "=", rec.x_espesor)]
                )
                if not allowed:
                    raise ValidationError(
                        "El espesor debe corresponder a uno de los valores permitidos "
                        "definidos en el mantenedor de espesores."
                    )

            if (rec.x_ancho not in (False, None) or rec.x_alto not in (False, None)) and not active_range:
                raise ValidationError(
                    "No existe una configuración activa de rangos para ancho y alto. "
                    "Revise Ventas > Parámetros."
                )

            if rec.x_ancho not in (False, None):
                if not (active_range.width_min <= rec.x_ancho <= active_range.width_max):
                    raise ValidationError(
                        f"El ancho debe estar entre {active_range.width_min} y {active_range.width_max}."
                    )

            if rec.x_alto not in (False, None):
                if not (active_range.length_min <= rec.x_alto <= active_range.length_max):
                    raise ValidationError(
                        f"El alto debe estar entre {active_range.length_min} y {active_range.length_max}."
                    )

    @api.model
    def _get_iva_tax(self, company):
        return self.env["account.tax"].search(
            [
                ("type_tax_use", "=", "sale"),
                ("amount_type", "=", "percent"),
                ("amount", "=", 19),
                ("company_id", "=", company.id),
                ("active", "=", True),
            ],
            limit=1,
        )

    @api.model_create_multi
    def create(self, vals_list):
        unit_uom = self.env.ref("uom.product_uom_unit", raise_if_not_found=False)
        for vals in vals_list:
            company = self.env.company
            if vals.get("order_id"):
                order = self.env["sale.order"].browse(vals["order_id"])
                if order.company_id:
                    company = order.company_id

            if unit_uom and not vals.get("product_uom"):
                vals["product_uom"] = unit_uom.id

            iva_tax = self._get_iva_tax(company)
            if iva_tax:
                vals["tax_id"] = [(6, 0, [iva_tax.id])]

        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        if "tax_id" not in vals:
            taxes_by_line = {}
            for line in self:
                iva_tax = self._get_iva_tax(line.company_id or line.order_id.company_id or self.env.company)
                if iva_tax:
                    taxes_by_line[line.id] = iva_tax.id

            result = super().write(vals)
            for line in self.filtered(lambda l: l.id in taxes_by_line):
                line.tax_id = [(6, 0, [taxes_by_line[line.id]])]
            return result

        return super().write(vals)
