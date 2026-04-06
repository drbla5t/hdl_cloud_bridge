#!/usr/bin/with-contenv bashio

echo "Starting HDL Buspro Add-on..."

export HDL_USERNAME="$(bashio::config 'hdl_user')"
export HDL_PASSWORD="$(bashio::config 'hdl_pass')"
export HDL_SERVER="$(bashio::config 'hdl_server')"

export MQTT_HOST="$(bashio::config 'mqtt_host')"
export MQTT_PORT="$(bashio::config 'mqtt_port')"
export MQTT_USER="$(bashio::config 'mqtt_user')"
export MQTT_PASS="$(bashio::config 'mqtt_pass')"

export POLL_INTERVAL="$(bashio::config 'poll_interval')"

HOME_NAMES_JSON="$(bashio::config 'home_names')"
export HDL_HOME_NAMES="${HOME_NAMES_JSON}"

echo "HDL user: ${HDL_USERNAME}"
echo "HDL server: ${HDL_SERVER}"
echo "MQTT host: ${MQTT_HOST}:${MQTT_PORT}"
echo "Poll interval: ${POLL_INTERVAL}"
echo "Home names: ${HDL_HOME_NAMES}"

python3 -m app.main