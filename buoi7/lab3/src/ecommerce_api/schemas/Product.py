from marshmallow import Schema, ValidationError, fields, validate, validates


class ProductCreateSchema(Schema):
    sku = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=32),
            validate.Regexp(r"^[A-Z0-9-]+$"),
        ],
    )
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    price_cents = fields.Integer(
        required=True, validate=validate.Range(min=0, max=10_000_000)
    )
    qty_in_stock = fields.Integer(load_default=0, validate=validate.Range(min=0))
    archived = fields.Boolean(load_default=False)
    description = fields.String(allow_none=True, validate=validate.Length(max=2000))

    @validates("name")
    def validate_name(self, value, **kwargs):
        if value.strip() == "":
            raise ValidationError("name trống")

    @validates("price_cents")
    def validate_price_cents(self, value, **kwargs):
        if value < 0:
            raise ValidationError("giá không hợp lệ")


class ProductUpdateSchema(Schema):
    sku = fields.String(
        validate=[
            validate.Length(min=3, max=32),
            validate.Regexp(r"^[A-Z0-9-]+$"),
        ]
    )
    name = fields.String(validate=validate.Length(min=1, max=255))
    price_cents = fields.Integer(validate=validate.Range(min=0, max=10_000_000))
    qty_in_stock = fields.Integer(validate=validate.Range(min=0))
    archived = fields.Boolean()
    description = fields.String(allow_none=True, validate=validate.Length(max=2000))

    @validates("name")
    def validate_name(self, value, **kwargs):
        if value.strip() == "":
            raise ValidationError("name trống")

    @validates("price_cents")
    def validate_price_cents(self, value, **kwargs):
        if value < 0:
            raise ValidationError("giá không hợp lệ")


class StockDecreaseSchema(Schema):
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))


class ProductQuerySchema(Schema):
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    size = fields.Integer(load_default=20, validate=validate.Range(min=1))


class ProductResponseSchema(Schema):
    id = fields.Integer()
    sku = fields.String()
    name = fields.String()
    price_cents = fields.Integer()
    qty_in_stock = fields.Integer()
    archived = fields.Boolean()
    description = fields.String(allow_none=True)
    created_at = fields.DateTime()


class ProductPageSchema(Schema):
    items = fields.List(fields.Nested(ProductResponseSchema), required=True)
    page = fields.Integer(required=True)
    size = fields.Integer(required=True)
    total = fields.Integer(required=True)


class ProductErrorSchema(Schema):
    code = fields.String(required=True)
    message = fields.String(required=True)
