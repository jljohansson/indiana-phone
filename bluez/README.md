
Setting up Pi from scratch:

Mosquitto:

sudo apt update && sudo apt install -y mosquitto mosquitto-clients

Listen for all topcis (-d is debug; more printouts)
mosquitto_sub -t '#'

Publish a message on the topic "indiana-jones"
mosquitto_pub -t indiana-jones -m "poison still fresh"

