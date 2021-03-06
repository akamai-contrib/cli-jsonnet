import os, os.path
import json
from .edgegrid import Session
from .logging import logger
from .jsonnet.papi.schema import Schema, SchemaConverter
from .jsonnet.papi.property import Property, PropertyConverter

def products(edgerc, section, contractId, accountSwitchKey=None, **kwargs):
  session = Session(edgerc, section, accountSwitchKey)
  response = session.get("/papi/v1/products", params={"contractId": contractId})
  products = response.json().get("products").get("items")
  print("\n".join(map(lambda p: "{productName}: {productId}".format(**p), products)))

def schema(edgerc, section, productId, ruleFormat="latest", accountSwitchKey=None, **kwargs):
  schema = Schema.get(edgerc, section, productId, ruleFormat, accountSwitchKey)
  converter = SchemaConverter(schema)
  converter.convert()
  print(converter.writer.getvalue())

def property(edgerc, section, productId, propertyName, propertyVersion="latest", standalone=True, file=None, ruleFormat="latest", accountSwitchKey=None, **kwargs):
  schema = Schema.get(edgerc, section, productId, ruleFormat, accountSwitchKey)

  if not standalone:
    converter = SchemaConverter(schema)
    converter.convert()
    schema_path = 'papi/{}/{}.libsonnet'.format(productId, ruleFormat) # TODO: make this a constant (shared with property.py)
    os.makedirs(os.path.dirname(schema_path), exist_ok=True)
    with open(schema_path, "w") as fd:
      fd.write(converter.writer.getvalue())

  property = None
  if file is None:
    property = Property.get(edgerc, section, propertyName, propertyVersion, ruleFormat, accountSwitchKey)
  else:
    with open(file, "r") as fd:
      data = json.loads(fd.read())
      property = Property(propertyName, data)

  converter = PropertyConverter(schema, property)
  converter.convert()
