{
    "name": "Personalizacion Modulo Ventas",
    "version": "18.0.1.0.0",
    "summary": "Agrega campos personalizados",
    "category": "Sales/Sales",
    "author": "Luciano Badilla",
    "license": "LGPL-3",
    "depends": [
        "sale_management",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sale_dimension_data.xml",
        "views/sale_dimension_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
}