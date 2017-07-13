from lgudap.client.protocol import Command, Query, Protocol
from lgudap.client.protocol import String, Integer


class HandleKeyInput(Command):
    value = String()


class HandleTouchMove(Command):
    x = Integer()
    y = Integer()


class HandleTouckClick(Command):
    pass


class HandleTouckWheel(Command):
    value = String()


class HandleChannelChange(Command):
    major = Integer()
    minor = Integer()
    source_index = Integer()
    physical_num = Integer()


class CurrentChannel(Query):
    pass


class ChannelList(Query):
    pass


class UIMode(Query):
    pass


class VolumeInfo(Query):
    pass


class NetRcu(Protocol):
    key_input = HandleKeyInput()
    touch_move = HandleTouchMove()
    touch_click = HandleTouckClick()
    channel_change = HandleChannelChange()
    cur_channel = CurrentChannel()
    volume_info = VolumeInfo()
    channel_list = ChannelList()
    context_ui = UIMode()
