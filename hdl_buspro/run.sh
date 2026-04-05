#!/usr/bin/with-contenv bashio

echo "Starting HDL Buspro Add-on..."

export HDL_USER=$(bashio::config 'hdl_user')
export HDL_PASS=$(bashio::config 'hdl_pass')

export MQTT_HOST=$(bashio::config 'mqtt_host')
export MQTT_PORT=$(bashio::config 'mqtt_port')
export MQTT_USER=$(bashio::config 'mqtt_user')
export MQTT_PASS=$(bashio::config 'mqtt_pass')

export POLL_INTERVAL=$(bashio::config 'poll_interval')

python3 -m app.main