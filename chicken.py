import audiocore
import board
import audiobusio

wave_file = open("wav/street_chicken.wav", "rb")
wave = audiocore.WaveFile(wave_file)



# M4 express
# D10 => 1st (LRC)
# D1  => 2nd (BCLK)
# D11 => 3rd (DIN)
# audio = audiobusio.I2SOut(board.D1, board.D10, board.D11)

# QT Py RP 2040
## audio = audiobusio.I2SOut(board.A1, board.A0, board.A2)

# Feather RP2040
audio = audiobusio.I2SOut(board.A0, board.A1, board.A2)


# A0 goes to first hole ==>  LRC   (second param)
# A1 goes to second hole ==> BLCK  (FIRST param)
# A2 goes to third hole ==>  DIN   (third param)

while True:
    audio.play(wave)
    while audio.playing:
        pass
