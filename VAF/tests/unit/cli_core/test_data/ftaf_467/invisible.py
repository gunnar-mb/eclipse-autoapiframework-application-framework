from datetime import timedelta

from .imported_models import interfaces
from vaf import vafpy

invisible = vafpy.ApplicationModule(name="Invisible", namespace="Snuggle")
invisible.add_provided_interface(instance_name="NakedStar", interface=interfaces.Adas.Interfaces.object_detection_list_interface)
invisible.add_consumed_interface(instance_name="AureliaBoriolis", interface=interfaces.Adas.Interfaces.object_detection_list_interface)
invisible.add_task(vafpy.Task(name="AllMyExes", period=timedelta(milliseconds=45)))
invisible.add_task(vafpy.Task(name="LivesInTexas", period=timedelta(milliseconds=111)))
