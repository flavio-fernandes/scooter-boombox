# SPDX-FileCopyrightText: 2022 John Park for Adafruit Industries
# SPDX-License-Identifier: MIT
# Adapted by Flaviof for some extra functionality

# Convert files to appropriate WAV format (mono, 22050 Hz, 16-bit signed)

import asyncio
import time
import board
import keypad
import audiocore
import audiomixer
import audiobusio
from digitalio import DigitalInOut, Direction
import supervisor
import microcontroller
from collections import namedtuple


SUSTAIN_SECS = 6

# pins used by keyboard
KEY_PINS = (board.D12, board.D6, board.D5)  # red:horn yellow:tricicle white:bell

# leds
LED_PINS = (board.MOSI, board.MISO)

WaveFile = namedtuple("WaveFile", "filename level")

# list of (samples to play, mixer gain level)
wav_files = (
    WaveFile("wav/airhorn.wav", 1.0),  # Honk sound 1  (button 1)
    WaveFile("wav/bike-horn.wav", 1.0),  # Honk around 2 (button 2)
    WaveFile("wav/chime.wav", 1.0),  # Honk sound 3 (button 3)
    # Looping Sound Effects
    WaveFile("wav/idle.wav", 0.5),
    WaveFile("wav/street_chicken.wav", 0.7),
    WaveFile("wav/gremlin_alarm.wav", 0.5),
    WaveFile("wav/amen_22k16b_160bpm.wav", 0.5),
    WaveFile("wav/dnb21580_22k16b_160bpm.wav", 0.5),
    WaveFile("wav/drumloopA_22k16b_160bpm.wav", 0.5),
    WaveFile("wav/femvoc_330662_half_22k16b_160bpm_01.wav", 0.5),
    WaveFile("wav/lion.wav", 0.5),
    WaveFile("wav/tequila.wav", 0.5),
    WaveFile("wav/undersea.wav", 0.5),
    WaveFile("wav/full_ring.wav", 0.5),
    WaveFile("wav/blank_number.wav", 0.5),
)


class State:
    def __init__(self):
        self.soft_dog = 0
        self.buttons_pressed_now = 0
        self.buttons_pressed_together = 0
        self.next_background_voice = len(KEY_PINS)
        self.next_background_enabled = False
        self.animate_leds = True
        self.next_animate_led = 0
        self.sustain_voice_enabled = False
        self.sustain_voices = [0] * len(wav_files)


leds = [DigitalInOut(led_pin) for led_pin in LED_PINS]
for led in leds:
    led.direction = Direction.OUTPUT
    led.value = True

audio = audiobusio.I2SOut(board.A0, board.A1, board.A2)
mixer = audiomixer.Mixer(
    voice_count=len(wav_files),
    sample_rate=22050,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
)
audio.play(mixer)  # attach mixer to audio playback

for i in range(len(wav_files)):  # start all samples at once for use w handle_mixer
    wave = audiocore.WaveFile(open(wav_files[i].filename, "rb"))
    mixer.voice[i].play(wave, loop=True)
    mixer.voice[i].level = 0

for led in leds:
    time.sleep(1)
    led.value = False


def toggle_background_mixer(state):
    assert len(KEY_PINS) < len(wav_files)
    for i in range(len(KEY_PINS), len(wav_files), 1):
        mixer.voice[i].level = 0

    # toggle on and off to have silence in between
    state.next_background_enabled = not state.next_background_enabled
    if not state.next_background_enabled:
        return

    mixer.voice[state.next_background_voice].level = wav_files[
        state.next_background_voice
    ].level
    state.next_background_voice += 1
    if state.next_background_voice >= len(wav_files):
        state.next_background_voice = len(KEY_PINS)


def toggle_animate_leds(state):
    state.animate_leds = not state.animate_leds


def toggle_sustain_voice(state):
    state.sustain_voice_enabled = not state.sustain_voice_enabled

    if not state.sustain_voice_enabled:
        for i in range(len(KEY_PINS)):
            mixer.voice[i].level = 0  # mute it
            state.sustain_voices[i] = 0


def handle_mixer(state, num, pressed):
    voice = mixer.voice[num]  # get mixer voice
    if pressed:
        voice.level = wav_files[num].level  # play at level in wav_file list

        # mark voice to skip sustaining
        state.sustain_voices[num] = -1

        state.buttons_pressed_now += 1
        state.buttons_pressed_together += 1

        # if all buttons are pressed, toggle background player
        if state.buttons_pressed_now == len(KEY_PINS):
            toggle_background_mixer(state)

    else:  # released

        if not state.sustain_voice_enabled:
            voice.level = 0  # mute it
        else:
            state.sustain_voices[num] = SUSTAIN_SECS  # mute it after sustain

        state.buttons_pressed_now -= 1
        if not state.buttons_pressed_now:
            # all buttons released
            toggle_animate_leds(state)

            # check and see how many buttons were pressed at the same time
            if state.buttons_pressed_together == 2:
                toggle_sustain_voice(state)

            state.buttons_pressed_together = 0


async def soft_dogwatch(state):
    # Note: this is mostly used to handle cases when there is an exception in
    # buttons_monitor that could not be handled. When this happens,
    # state.soft_dog will stop increasing and we will know it is time to panic.
    soft_dogwatch_interval = 60
    while True:
        before_soft_dog = state.soft_dog
        await asyncio.sleep(soft_dogwatch_interval)
        if before_soft_dog == state.soft_dog:
            print(
                f"state.soft_dog stuck at {before_soft_dog}"
                " after {soft_dogwatch_interval} seconds"
            )
            await asyncio.sleep(5)
            # bye bye cruel world
            microcontroller.reset()

        state.soft_dog = 0


async def sustain_ager(state):
    while True:
        await asyncio.sleep(1)
        if not state.sustain_voice_enabled:
            continue
        for i in range(len(KEY_PINS)):
            if state.sustain_voices[i] > 0:
                state.sustain_voices[i] -= 1

            if not state.sustain_voices[i]:
                mixer.voice[i].level = 0  # mute it


async def animate_leds(state):
    while True:
        await asyncio.sleep(0.333)
        for i in range(len(leds)):
            leds[i].value = i == state.next_animate_led and state.animate_leds
        state.next_animate_led = (state.next_animate_led + 1) % len(leds)


async def buttons_monitor(state):
    km = keypad.Keys(KEY_PINS, value_when_pressed=False, pull=True)
    while True:
        state.soft_dog += 1
        await asyncio.sleep(0.1)
        event = km.events.get()
        if event:
            if event.key_number < len(wav_files):
                if event.pressed:
                    handle_mixer(state, event.key_number, True)

                if event.released:
                    handle_mixer(state, event.key_number, False)


async def main():
    state = State()

    # start Looping Sound Effects
    toggle_background_mixer(state)

    soft_dogwatch_task = asyncio.create_task(soft_dogwatch(state))
    animate_leds_task = asyncio.create_task(animate_leds(state))
    sustain_ager_task = asyncio.create_task(sustain_ager(state))
    buttons_monitor_task = asyncio.create_task(buttons_monitor(state))
    await asyncio.gather(
        soft_dogwatch_task,
        animate_leds_task,
        sustain_ager_task,
        buttons_monitor_task,
    )


supervisor.runtime.autoreload = False
asyncio.run(main())
