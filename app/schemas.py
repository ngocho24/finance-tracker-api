from marshmallow import Schema, fields, validate

class TransactionSchema(Schema):
    id = fields.Int(dump_only=True)
    amount = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=0.01))
    description = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    category = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    type = fields.Str(required=True, validate=validate.OneOf(["income", "expense"]))
    date = fields.DateTime(dump_only=True)

# Initialize schemas
transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)