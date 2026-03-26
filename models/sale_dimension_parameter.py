from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleDimensionThickness(models.Model):
    _name = "sale.dimension.thickness"
    _description = "Espesor permitido para ventas"
    _order = "value asc"

    value = fields.Integer(string="Espesor (mm)", required=True)
    active = fields.Boolean(string="Activo", default=True)
    note = fields.Char(string="Observación")

    _sql_constraints = [
        (
            "sale_dimension_thickness_value_unique",
            "unique(value)",
            "Ya existe un espesor con ese valor.",
        ),
        (
            "sale_dimension_thickness_value_positive",
            "check(value > 0)",
            "El espesor debe ser mayor que cero.",
        ),
    ]

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, f"{rec.value} mm"))
        return result


class SaleDimensionRange(models.Model):
    _name = "sale.dimension.range"
    _description = "Rangos permitidos para ancho y alto en ventas"
    _order = "id desc"

    name = fields.Char(string="Nombre", required=True, default="Configuración general")
    active = fields.Boolean(string="Activo", default=True)

    width_min = fields.Integer(string="Ancho mínimo", required=True, default=600)
    width_max = fields.Integer(string="Ancho máximo", required=True, default=1150)
    length_min = fields.Integer(string="Alto mínimo", required=True, default=2000)
    length_max = fields.Integer(string="Alto máximo", required=True, default=2400)

    @api.constrains("width_min", "width_max", "length_min", "length_max")
    def _check_min_max(self):
        for rec in self:
            if rec.width_min > rec.width_max:
                raise ValidationError("El ancho mínimo no puede ser mayor que el ancho máximo.")
            if rec.length_min > rec.length_max:
                raise ValidationError("El alto mínimo no puede ser mayor que el alto máximo.")

    @api.constrains("active")
    def _check_single_active_record(self):
        for rec in self.filtered("active"):
            count = self.search_count([("active", "=", True)])
            if count > 1:
                raise ValidationError(
                    "Solo puede existir una configuración de rangos activa a la vez."
                )