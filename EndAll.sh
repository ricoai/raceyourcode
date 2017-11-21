#!/bin/bash
sudo killall -9 python
python -c "import ThunderBorg; t=ThunderBorg.ThunderBorg(); t.Init(); t.MotorsOff()"
fg
