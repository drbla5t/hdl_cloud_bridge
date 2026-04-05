from app.handlers import light as cmd_light
from app.handlers import curtain as cmd_curtain
from app.handlers import climate as cmd_climate

from app.state_handlers import light as state_light
from app.state_handlers import curtain as state_curtain
from app.state_handlers import climate as state_climate

from app.discovery_handlers import light as disc_light
from app.discovery_handlers import curtain as disc_curtain
from app.discovery_handlers import climate as disc_climate


DEVICE_REGISTRY = {
    "light.switch": {
        "command": cmd_light.handle_light_command,
        "state": state_light.publish,
        "discovery": disc_light.build,
    },
    "curtain.switch": {
        "command": cmd_curtain.handle_curtain_command,
        "state": state_curtain.publish,
        "discovery": disc_curtain.build,
    },
    "hvac.ac": {
        "command": cmd_climate.handle_climate_command,
        "state": state_climate.publish,
        "discovery": disc_climate.build,
    },
}