#!/usr/bin/python
# requires Silan-SC7314_Driver.py
import SilanSC7314_Driver

myic = SilanSC7314_Driver.sc7314()
myic.set_input(1)
myic.set_volume(20)
