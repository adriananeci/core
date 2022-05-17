"""Tests for Logger Websocket API commands."""
import logging

from homeassistant.components.logger.const import DOMAIN
from homeassistant.components.websocket_api import const
from homeassistant.setup import async_setup_component


async def test_integration_log_info(hass, hass_ws_client, hass_admin_user):
    """Test fetching integration log info."""

    assert await async_setup_component(hass, "logger", {})

    logging.getLogger("homeassistant.components.http").setLevel(logging.DEBUG)
    logging.getLogger("homeassistant.components.websocket_api").setLevel(logging.DEBUG)

    websocket_client = await hass_ws_client()
    await websocket_client.send_json({"id": 7, "type": "logger/log_info"})

    msg = await websocket_client.receive_json()
    assert msg["id"] == 7
    assert msg["type"] == const.TYPE_RESULT
    assert msg["success"]
    assert {"domain": "http", "level": logging.DEBUG} in msg["result"]
    assert {"domain": "websocket_api", "level": logging.DEBUG} in msg["result"]


async def test_integration_log_level_logger_not_loaded(
    hass, hass_ws_client, hass_admin_user
):
    """Test setting integration log level."""
    websocket_client = await hass_ws_client()
    await websocket_client.send_json(
        {
            "id": 7,
            "type": "logger/log_level",
            "integration": "websocket_api",
            "level": logging.DEBUG,
            "persistence": "none",
        }
    )

    msg = await websocket_client.receive_json()
    assert msg["id"] == 7
    assert msg["type"] == const.TYPE_RESULT
    assert not msg["success"]


async def test_integration_log_level(hass, hass_ws_client, hass_admin_user):
    """Test setting integration log level."""
    websocket_client = await hass_ws_client()
    assert await async_setup_component(hass, "logger", {})

    await websocket_client.send_json(
        {
            "id": 7,
            "type": "logger/integration_log_level",
            "integration": "websocket_api",
            "level": "DEBUG",
            "persistence": "none",
        }
    )

    msg = await websocket_client.receive_json()
    assert msg["id"] == 7
    assert msg["type"] == const.TYPE_RESULT
    assert msg["success"]

    assert hass.data[DOMAIN]["overrides"] == {
        "homeassistant.components.websocket_api": logging.DEBUG
    }


async def test_integration_log_level_unknown_integration(
    hass, hass_ws_client, hass_admin_user
):
    """Test setting integration log level for an unknown integration."""
    websocket_client = await hass_ws_client()
    assert await async_setup_component(hass, "logger", {})

    await websocket_client.send_json(
        {
            "id": 7,
            "type": "logger/integration_log_level",
            "integration": "websocket_api_123",
            "level": "DEBUG",
            "persistence": "none",
        }
    )

    msg = await websocket_client.receive_json()
    assert msg["id"] == 7
    assert msg["type"] == const.TYPE_RESULT
    assert not msg["success"]


async def test_module_log_level(hass, hass_ws_client, hass_admin_user):
    """Test setting integration log level."""
    websocket_client = await hass_ws_client()
    assert await async_setup_component(
        hass,
        "logger",
        {"logger": {"logs": {"homeassistant.components.other_component": "warning"}}},
    )

    await websocket_client.send_json(
        {
            "id": 7,
            "type": "logger/log_level",
            "module": "homeassistant.components.websocket_api",
            "level": "DEBUG",
            "persistence": "none",
        }
    )

    msg = await websocket_client.receive_json()
    assert msg["id"] == 7
    assert msg["type"] == const.TYPE_RESULT
    assert msg["success"]

    assert hass.data[DOMAIN]["overrides"] == {
        "homeassistant.components.websocket_api": logging.DEBUG,
        "homeassistant.components.other_component": logging.WARNING,
    }


async def test_module_log_level_override(hass, hass_ws_client, hass_admin_user):
    """Test override yaml integration log level."""
    websocket_client = await hass_ws_client()
    assert await async_setup_component(
        hass,
        "logger",
        {"logger": {"logs": {"homeassistant.components.websocket_api": "warning"}}},
    )

    assert hass.data[DOMAIN]["overrides"] == {
        "homeassistant.components.websocket_api": logging.WARNING
    }

    await websocket_client.send_json(
        {
            "id": 6,
            "type": "logger/log_level",
            "module": "homeassistant.components.websocket_api",
            "level": "ERROR",
            "persistence": "none",
        }
    )

    msg = await websocket_client.receive_json()
    assert msg["id"] == 6
    assert msg["type"] == const.TYPE_RESULT
    assert msg["success"]

    assert hass.data[DOMAIN]["overrides"] == {
        "homeassistant.components.websocket_api": logging.WARNING
    }

    await websocket_client.send_json(
        {
            "id": 7,
            "type": "logger/log_level",
            "module": "homeassistant.components.websocket_api",
            "level": "DEBUG",
            "persistence": "none",
        }
    )

    msg = await websocket_client.receive_json()
    assert msg["id"] == 7
    assert msg["type"] == const.TYPE_RESULT
    assert msg["success"]

    assert hass.data[DOMAIN]["overrides"] == {
        "homeassistant.components.websocket_api": logging.DEBUG
    }

    await websocket_client.send_json(
        {
            "id": 8,
            "type": "logger/log_level",
            "module": "homeassistant.components.websocket_api",
            "level": "NOTSET",
            "persistence": "none",
        }
    )

    msg = await websocket_client.receive_json()
    assert msg["id"] == 8
    assert msg["type"] == const.TYPE_RESULT
    assert msg["success"]

    assert hass.data[DOMAIN]["overrides"] == {
        "homeassistant.components.websocket_api": logging.WARNING
    }
