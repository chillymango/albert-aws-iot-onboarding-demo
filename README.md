# AWS IoT Core Onboarding Project

This project is Albert's onboarding demo.

The goal is to get the customer experience when using the IoT backend.

This project simulates a few factory sensors that telemeter a vacuum chamber.
The project simulates three pressure sensors (redundant), as well as an Argon gas detector.

For this demo, we are interested in the following:
* sending alerts for when argon concentration is high while the chamber is under high vacuum
* sending alerts for when the pressure sensors deviate by high amounts

The engineering justification for this is that high concentrations of argon in the vacuum chamber

while under vacuum will have strong adverse effects on the manufacturing process being performed in the chamber. However, while the chamber is not under vacuum, the concentration of argon

measured is allowed / expected to be high due to relatively high trace volumes of it in the atmosphere.

Pressure sensors will report pressure in atmospheres.

Gas sensors will report concentrations in ppm (parts per million).

This demo consists of several components:
* a Sensor base class which publishes MQTT messages to the message broker
* a Listener class which collects all messages issued on a specified topic
* a run script which creates three pressure sensors, an argon gas sensor, and runs through a specified scenario

This demo consists of the following scenarios:

* pressure sensors functioning normally, pressure is ambient (1atm), argon concentration high. Expected outcome is no alerts.
* pressure sensors functioning normally, pressure is vacuum (0atm), argon concentration low. Expected outcome is no alerts.
* pressure sensors functioning normally, pressure is vacuum (0atm), argon concentration high. Expected outcome is a gas alert.
* pressure sensors show one fault, pressure is ambient (1atm), argon concentration high. Expected outcome is a sensor fault alert.
* pressure sensors show one fault, pressure is vacuum (0atm), argon concentration low. Expected outcome is both a gas alert and a sensor fault alert.

In the backend, the following must be set up:
* keys provisioned for each IoT device
* Security Policy altered to allow telemetry/* topics to pubsub
* Security Policy altered to allow client ID matching the device name to connect
* rules engine set up to monitor argon concentration
* rules engine set up to monitor pressure sensor failure
* create SQS topic for SNS notifications

NOTE: the keys for the IoT devices **SHOULD NOT** be included in this repo.
The current demo expects valid keys / certs at the following paths:
* data/gas-sensor-a.cert.pem
* data/gas-sensor-a.crt
* data/gas-sensor-a.private.key
* data/pressure-sensor-a.cert.pem
* data/pressure-sensor-a.crt
* data/pressure-sensor-a.private.key
* data/pressure-sensor-b.cert.pem
* data/pressure-sensor-b.crt
* data/pressure-sensor-b.private.key
* data/pressure-sensor-c.cert.pem
* data/pressure-sensor-c.crt
* data/pressure-sensor-c.private.key
