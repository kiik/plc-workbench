# blinker

Toolchain hello world: `Lamp` (`%QX0.0`) blinks at 1 Hz while `Enable` (`%QX0.1`, starts on) is
on; `Blinks` (`%QW0`) counts the flashes.

```sh
tools/openplc/openplc.py up
tools/openplc/openplc.py deploy blinker
tools/openplc/openplc.py watch -p blinker --seconds 3
tools/openplc/openplc.py write -p blinker Enable=0
```
