# scooter-boombox

#### Remix of Adafruit's Soundboard Speaker for Bikes & Scooters

This project is an implementation of the project described in
### [Soundboard Speaker for Bikes & Scooters](https://learn.adafruit.com/soundboard-speaker-for-bikes-scooters?view=all)
by [Ruiz Brothers](https://learn.adafruit.com/u/pixil3d)

![scooter-boombox](https://live.staticflickr.com/65535/53101106091_efc3df6b45.jpg)

You can see more [pictures here :art:](https://www.flickr.com/gp/38447095@N00/1dYq76b2zK).

# Usage

### Removing all files from the CIRCUITPY drive.

```
# NOTE: Do not do this before backing up all files!!!
>>> import storage ; storage.erase_filesystem()
```

### Copying files from cloned repo to CIRCUITPY drive
First, get to the REPL prompt so the board will not auto-restart as
you copy files into it.

Assuming that [Feather](https://www.adafruit.com/category/943) is mounted under /Volumes/CIRCUITPY, do:

```
$  cd ${THIS_REPO_DIR}
$  [ -e ./code.py ] && \
   [ -d /Volumes/CIRCUITPY/ ] && \
   rm -rf /Volumes/CIRCUITPY/*.py && \
   (tar czf - *) | ( cd /Volumes/CIRCUITPY ; tar xzvf - ) && \
   echo ok || echo not_okay
```

### Libraries

Use [circup](https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup)
to install these libraries:

```text
$ python3 -m venv .env && source ./.env/bin/activate && \
  pip install --upgrade pip

$ pip3 install circup
$ circup install asyncio
```

After following the steps above, the output should look like this:
```text
$ cat /Volumes/CIRCUITPY/boot_out.txt
Adafruit CircuitPython 8.2.2 on 2023-07-31; Adafruit Feather RP2040 with rp2040
Board ID:adafruit_feather_rp2040
UID:XXXXXXXXXX

$ circup freeze | sort
Found device at /Volumes/CIRCUITPY, running CircuitPython 8.2.2.
adafruit_ticks==1.0.11
asyncio==0.5.23

$ ls /Volumes/CIRCUITPY/
LICENSE		boot_out.txt	code.py		scooter.py	wav
README.md	chicken.py	lib		settings.toml

$ ls /Volumes/CIRCUITPY/lib
adafruit_ticks.mpy	asyncio
```

At this point, all needed files should be in place and all that is needed is to allow code.py to run. From the Circuit Python serial console:

```text
>>  <CTRL-D>
soft reboot
...
```

Try pressing all three buttons at the same time.
It should play through the [wav files](https://github.com/flavio-fernandes/scooter-boombox/blob/92c751c766d8e8b3f3654deb45b6e22a935ac774/scooter.py#L31-L48).

Pressing 2 buttons will toggle the sustain feature. What I mean by that is that the playing of the sound will carry on for [an additional number of seconds](https://github.com/flavio-fernandes/scooter-boombox/blob/92c751c766d8e8b3f3654deb45b6e22a935ac774/scooter.py#L20) after the button is released.

Enjoy the ride!
