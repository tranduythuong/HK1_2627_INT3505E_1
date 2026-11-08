from marshmallow import Schema, ValidationError, fields, validate, validates


class OrderItemCreateSchema(Schema):
    product_id = fields.Integer(required=True, validate=validate.Range(min=1))
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))


class OrderCreateSchema(Schema):
    items = fields.List(
        fields.Nested(OrderItemCreateSchema),
        required=True,
        validate=validate.Length(min=1, max=100),
    )

    @validates("items")
    def validate_distinct_products(self, items, **kwargs):
        product_ids = [item["product_id"] for item in items]
        if len(product_ids) != len(set(product_ids)):
            raise ValidationError("Each product may appear only once in an order.")


class OrderItemResponseSchema(Schema):
    id = fields.Integer()
    product_id = fields.Integer()
    quantity = fields.Integer()
    unit_price_cents = fields.Integer()
    product_name = fields.String(attribute="product.name")
    sku = fields.String(attribute="product.sku")


class OrderResponseSchema(Schema):
    id = fields.Integer()
    created_at = fields.DateTime()
    items = fields.List(fields.Nested(OrderItemResponseSchema))


class OrderErrorSchema(Schema):
    code = fields.String(required=True)
    message = fields.String(required=True)
