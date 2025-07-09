from datetime import timedelta

from .imported_models import interfaces
from vaf import vafpy

mockery = vafpy.ApplicationModule(name="Mockery", namespace="Snuggle")
mockery.add_consumed_interface(instance_name="McDonalds", interface=interfaces.Adas.Interfaces.object_detection_list_interface)
mockery.add_task(vafpy.Task(name="California", period=timedelta(milliseconds=121)))
mockery.add_task(vafpy.Task(name="Yorkies", period=timedelta(milliseconds=322)))
