# BTicinoAlerter

When working at my desk I want a visual alert when someone rings the doorbell because I work with headphones on.
On my desk is a Pico W with an LED ring that can light up if you call it over the network (Server code).

Initially I hacked my BTicino c100x videofoon and added code to call the server but this kept failing.
The custom firmware on the BTicino kept reverting to the unmodified version and the system broke.

The BTicino has a port however to attach up an external buzzer/ringer and now I'm using this instead.
I've hooked up a microcontroller (Trigger code) to this and it calls the server instead.