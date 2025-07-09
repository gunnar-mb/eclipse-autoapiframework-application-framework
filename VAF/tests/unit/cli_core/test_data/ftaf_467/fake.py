from datetime import timedelta

from .imported_models import interfaces
from vaf import vafpy

fake = vafpy.ApplicationModule(name="Fake", namespace="Snuggle")
fake.add_provided_interface(instance_name="KentuckyFriedChicken", interface=interfaces.Adas.Interfaces.object_detection_list_interface)
fake.add_task(vafpy.Task(name="SweetHomeAlabama", period=timedelta(milliseconds=67)))
