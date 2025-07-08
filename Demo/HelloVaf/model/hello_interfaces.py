from vaf import BaseTypes, vafpy

interface = vafpy.ModuleInterface(name="HelloWorldIf", namespace="demo")
interface.add_data_element("Message", datatype=BaseTypes.STRING)
interface.add_operation("SetMsgId", in_parameter={"MsgId": BaseTypes.UINT8_T})
