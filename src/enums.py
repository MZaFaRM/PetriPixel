from enum import Enum


class NeuronType(Enum):
    SENSOR = "sensor"
    HIDDEN = "hidden"
    ACTUATOR = "actuator"
    BIAS = "bias"

    # Other
    CONN = "connection"

class Defence(Enum):
    NONE = "None"
    SHIELDLING = "Shieldling"
    SWORDLING = "Swordling"
    CAMOUFLING = "Camoufling"


class MatingState(Enum):
    MINOR = -1
    NOT_READY = 0
    READY = 1
    MATING = 2
    WAITING = 3

class SurfDesc(Enum):
    SURFACE = "surface"
    CLICKED_SURFACE = "clicked_surface"
    CURRENT_SURFACE = "current_surface"
    RECT = "rect"
    ABSOLUTE_RECT = "absolute_rect"


class Attributes(Enum):
    BASE_POPULATION = "_base_population"
    SPECIES = "_species"
    DEFENSE_MECHANISM = "_defense_mechanism"
    DOMAIN = "_domain"
    VISION_RADIUS = "_vision_radius"
    SIZE = "_size"
    AGE_OF_MATURITY = "_age_of_maturity"
    COLOR = "_color"
    MAX_SPEED = "_max_speed"
    MAX_ENERGY = "_max_energy"
    MAX_LIFESPAN = "_max_lifespan"


class EventType(Enum):
    NAVIGATION = "navigation"
    OTHER = "other"
    GENESIS = "genesis"
    RESTART_SIMULATION = "restart_simulation"


class Shapes(Enum):
    CIRCLE = "circle"
    SQUARE = "square"
    TRIANGLE = "triangle"
    PENTAGON = "pentagon"


class MessagePacket:
    def __init__(
        self,
        msg_type: EventType,
        value: str,
        context: dict | list = None,
    ) -> None:
        self.msg_type = msg_type
        self.value = value
        self.context = context or {}

    def __eq__(self, value):
        try:
            return self.msg_type == value.msg_type and self.value == value.value
        except Exception:
            return False

    def __str__(self):
        return f"{self.msg_type}_{self.value}".lower()

    def __repr__(self):
        return f"Packet(type={self.msg_type.name}, value={self.value}, context={self.context})"


# class MessagePackets:
#     def __init__(self, *packets: MessagePacket):
#         self.packets = list(packets)

#     def __contains__(self, packet):
#         if not isinstance(packet, MessagePacket):
#             return False
#         return any(
#             existing_packet.msg_type == packet.msg_type
#             and existing_packet.value == packet.value
#             for existing_packet in self.packets
#         )

#     def index(self, packet):
#         if not isinstance(packet, MessagePacket):
#             raise TypeError("Argument must be an instance of MessagePacket.")
#         for i, existing_packet in enumerate(self.packets):
#             if existing_packet == packet:
#                 return i
#         raise ValueError("Packet not found in MessagePackets.")

#     def pop(self, index):
#         return self.packets.pop(index)

#     def __getitem__(self, index):
#         return self.packets[index]

#     def __setitem__(self, index, value):
#         if not isinstance(value, MessagePacket):
#             raise TypeError("Value must be an instance of MessagePacket.")
#         self.packets[index] = value

#     def __repr__(self):
#         return " ".join(repr(packet) for packet in self.packets)
