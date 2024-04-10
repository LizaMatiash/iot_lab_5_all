from marshmallow import Schema, fields
from .accelerometer_schema import AccelerometerSchema
from .location_schema import GpsSchema
# from ..domain.aggregated_data import AggregatedData


class AggregatedDataSchema(Schema):
    accelerometer = fields.Nested(AccelerometerSchema)
    gps = fields.Nested(GpsSchema)
    timestamp = fields.DateTime("iso")
