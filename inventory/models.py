# inventory/models.py

from django.db import models

class Material(models.Model):
    material_code = models.CharField(max_length=100)
    batch_code = models.CharField(max_length=100)
    storage_location = models.CharField(max_length=100)
    material_description = models.TextField()
    quantity = models.FloatField()
    unit_of_measure = models.CharField(max_length=50)
    value = models.FloatField(null=True, blank=True)
    department = models.CharField(max_length=100)
    batch_date = models.DateField()
    party_name = models.CharField(max_length=100, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    date_of_clearing = models.DateField(null=True, blank=True)
    person = models.CharField(max_length=100, null=True, blank=True)
    batch_ageing = models.IntegerField()
    material_broad_group_desc = models.CharField(max_length=100)

    class Meta:
        unique_together = ('material_code', 'batch_code')

    def __str__(self):
        return f'{self.material_code} - {self.batch_code}'
