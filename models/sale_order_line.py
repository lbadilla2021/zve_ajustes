from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    x_espesor = fields.Integer(string="Espesor")
    x_ancho = fields.Integer(string="Ancho")
    x_alto = fields.Integer(string="Alto")

    @api.constrains("x_espesor", "x_ancho", "x_alto")
    def _check_dimension_rules(self):
        Thickness = self.env["sale.dimension.thickness"]
        Range = self.env["sale.dimension.range"]

        active_range = Range.search([("active", "=", True)], limit=1)

        for rec in self:
            # Espesor: si se informa, debe existir dentro del mantenedor activo
            if rec.x_espesor not in (False, None):
                allowed = Thickness.search_count(
                    [("active", "=", True), ("value", "=", rec.x_espesor)]
                )
                if not allowed:
                    raise ValidationError(
                        "El espesor debe corresponder a uno de los valores permitidos "
                        "definidos en el mantenedor de espesores."
                    )

            # Si se informa ancho/alto, debe existir una configuración activa
            if (rec.x_ancho not in (False, None) or rec.x_alto not in (False, None)) and not active_range:
                raise ValidationError(
                    "No existe una configuración activa de rangos para ancho y alto. "
                    "Revise Ventas > Parámetros de dimensiones."
                )

            # Ancho
            if rec.x_ancho not in (False, None):
                if not (active_range.width_min <= rec.x_ancho <= active_range.width_max):
                    raise ValidationError(
                        f"El ancho debe estar entre {active_range.width_min} y {active_range.width_max}."
                    )

            # Alto
            if rec.x_alto not in (False, None):
                if not (active_range.length_min <= rec.x_alto <= active_range.length_max):
                    raise ValidationError(
                        f"El alto debe estar entre {active_range.length_min} y {active_range.length_max}."
                    )