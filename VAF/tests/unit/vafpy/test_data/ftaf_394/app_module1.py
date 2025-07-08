from datetime import timedelta

from silkit import Vcandrive

from vaf import vafpy

app_module1 = vafpy.ApplicationModule(name="AppModule1", namespace="demo")
app_module1.add_consumed_interface(instance_name="OcclusionMapConsumer", interface=Vcandrive.service_occlusion_map)
app_module1.add_task(vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200)))
