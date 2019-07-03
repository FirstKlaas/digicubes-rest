from tortoise.models import Model
import  tortoise.fields 

class ApiKeyModel(Model):

    apikey = fields.CharField(24, unique=True, null=False)
    valid_from = fields.DateField()
    valid_until = fields.DateField()

    clas Meta():
        table="apikey"