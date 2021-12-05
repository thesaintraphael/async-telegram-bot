from tortoise import models, fields


class User(models.Model):

    tg_id = fields.CharField(max_length=255)
    name = fields.CharField(max_length=255)
    date_subcribed = fields.DatetimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
