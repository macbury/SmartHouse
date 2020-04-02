"""Websocket API for Node-RED."""
import json
import logging

import voluptuous as vol

from homeassistant.components.websocket_api import (
    async_register_command,
    async_response,
    event_message,
    require_admin,
    result_message,
    websocket_command,
)
from homeassistant.const import (
    CONF_ID,
    CONF_NAME,
    CONF_STATE,
    CONF_TYPE,
    CONF_WEBHOOK_ID,
)
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.typing import HomeAssistantType

from .const import (
    CONF_ATTRIBUTES,
    CONF_COMPONENT,
    CONF_CONFIG,
    CONF_DEVICE_INFO,
    CONF_NODE_ID,
    CONF_REMOVE,
    CONF_SERVER_ID,
    DOMAIN,
    NODERED_DISCOVERY,
    NODERED_ENTITY,
    VERSION,
)

_LOGGER = logging.getLogger(__name__)


def register_websocket_handlers(hass: HomeAssistantType):
    """Register the websocket handlers."""

    async_register_command(hass, websocket_version)
    async_register_command(hass, websocket_webhook)
    async_register_command(hass, websocket_discovery)
    async_register_command(hass, websocket_entity)


@require_admin
@websocket_command(
    {
        vol.Required(CONF_TYPE): "nodered/discovery",
        vol.Required(CONF_COMPONENT): cv.string,
        vol.Required(CONF_SERVER_ID): cv.string,
        vol.Required(CONF_NODE_ID): cv.string,
        vol.Optional(CONF_CONFIG, default={}): dict,
        vol.Optional(CONF_STATE): vol.Any(bool, str, int, float),
        vol.Optional(CONF_ATTRIBUTES): dict,
        vol.Optional(CONF_REMOVE): bool,
        vol.Optional(CONF_DEVICE_INFO): dict,
    }
)
def websocket_discovery(hass, connection, msg):
    """Sensor command."""
    async_dispatcher_send(
        hass, NODERED_DISCOVERY.format(msg[CONF_COMPONENT]), msg, connection
    )
    connection.send_message(result_message(msg[CONF_ID], {"success": True}))


@require_admin
@websocket_command(
    {
        vol.Required(CONF_TYPE): "nodered/entity",
        vol.Required(CONF_SERVER_ID): cv.string,
        vol.Required(CONF_NODE_ID): cv.string,
        vol.Required(CONF_STATE): vol.Any(bool, str, int, float),
        vol.Optional(CONF_ATTRIBUTES, default={}): dict,
    }
)
def websocket_entity(hass, connection, msg):
    """Sensor command."""

    async_dispatcher_send(
        hass, NODERED_ENTITY.format(msg[CONF_SERVER_ID], msg[CONF_NODE_ID]), msg
    )
    connection.send_message(result_message(msg[CONF_ID], {"success": True}))


@require_admin
@websocket_command({vol.Required(CONF_TYPE): "nodered/version"})
def websocket_version(hass, connection, msg):
    """Version command."""

    connection.send_message(result_message(msg[CONF_ID], VERSION))


@require_admin
@async_response
@websocket_command(
    {
        vol.Required(CONF_TYPE): "nodered/webhook",
        vol.Required(CONF_WEBHOOK_ID): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_SERVER_ID): cv.string,
    }
)
async def websocket_webhook(hass, connection, msg):
    """Create webhook command."""
    webhook_id = msg[CONF_WEBHOOK_ID]

    @callback
    async def handle_webhook(hass, id, request):
        """Handle webhook callback."""
        body = await request.text()
        try:
            payload = json.loads(body) if body else {}
        except ValueError:
            payload = body

        data = {"payload": payload, "headers": dict(request.headers)}

        _LOGGER.debug(f"Webhook received {id[:15]}..: {data}")
        connection.send_message(event_message(msg[CONF_ID], {"data": data}))

    def remove_webhook() -> None:
        """Remove webhook command."""
        try:
            hass.components.webhook.async_unregister(webhook_id)

        except ValueError:
            pass

        _LOGGER.info(f"Webhook removed: {webhook_id[:15]}..")
        connection.send_message(result_message(msg[CONF_ID], {"success": True}))

    try:
        hass.components.webhook.async_register(
            DOMAIN, msg[CONF_NAME], webhook_id, handle_webhook
        )
    except ValueError:
        connection.send_message(result_message(msg[CONF_ID], {"success": False}))
        return

    _LOGGER.info(f"Webhook created: {webhook_id[:15]}..")
    connection.subscriptions[msg[CONF_ID]] = remove_webhook
    connection.send_message(result_message(msg[CONF_ID], {"success": True}))
