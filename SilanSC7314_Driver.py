#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Inspired (and partly stolen) from the fantastic HD74480 LCD / RPi_I2C_driver by Denis Pleic and others
# http://www.recantha.co.uk/blog/?p=4849
#

Made available under GNU GENERAL PUBLIC LICENSE

# Driver for Silan SC7314 I2C 4-CH Audio Processor/Switcher IC
# By Charles Pillar
# 2020-07-31, ver 0.1

"""
#
#
import smbus
from time import *

class i2c_device:
   def __init__(self, addr, port=0):
      self.addr = addr
      self.bus = smbus.SMBus(port)

# Write a single command
   def write_cmd(self, cmd):
      self.bus.write_byte(self.addr, cmd)
      sleep(0.0001)

# Write a command and argument
   def write_cmd_arg(self, cmd, data):
      self.bus.write_byte_data(self.addr, cmd, data)
      sleep(0.0001)

# Write a block of data
   def write_block_data(self, cmd, data):
      self.bus.write_block_data(self.addr, cmd, data)
      sleep(0.0001)

# Read a single byte
   def read(self):
      return self.bus.read_byte(self.addr)

# Read
   def read_data(self, cmd):
      return self.bus.read_byte_data(self.addr, cmd)

# Read a block of data
   def read_block_data(self, cmd):
      return self.bus.read_block_data(self.addr, cmd)



# SC7314 Address
ADDRESS = 0x44

# base command bits
#SET_VOLUME =    0b00000000
#SET_SPK_ATT_L = 0b11000000
#SET_SPK_ATT_R = 0b11100000
#SET_AUDIO_SW =  0b01000000
#SET_BASS_CTRL = 0b11000000
#SET_TREBLE_CTRL=0b01110000
SET_VOLUME =    0x00
SET_SPK_ATT_L = 0xC0
SET_SPK_ATT_R = 0xE0
SET_AUDIO_SW =  0x40
SET_BASS_CTRL = 0x60
SET_TREBLE_CTRL=0x70

INPUT_1 = 0x00
INPUT_2 = 0x01
INPUT_3 = 0x02
INPUT_4 = 0x03

LOUDNESS_ON  = 0x00
LOUDNESS_OFF = 0x04

GAIN_0 = 0x18
GAIN_1 = 0x10
GAIN_2 = 0x08
GAIN_3 = 0x00

# Major Volume Adjust
VOL_00 = 0b00111000
VOL_10 = 0b00110000
VOL_20 = 0b00101000
VOL_30 = 0b00100000
VOL_40 = 0b00011000
VOL_50 = 0b00010000
VOL_60 = 0b00001000
VOL_70 = 0b00000000
# Minor Volume Adjust
VOL_01 = 0b00000111
VOL_02 = 0b00000110
VOL_03 = 0b00000101
VOL_04 = 0b00000100
VOL_05 = 0b00000011
VOL_06 = 0b00000010
VOL_07 = 0b00000001
VOL_08 = 0b00000000

#En = 0b00000100 # Enable bit
#Rw = 0b00000010 # Read/Write bit
#Rs = 0b00000001 # Register select bit

class sc7314:
   #initializes objects and SC7314
   #it seems like the SC7314 may remember settings beyond power cycle
   #(it's difficult to cleanly power-cycle the one I'm testing with
   # making this difficult to test). If that is the case, then these
   # values will not match the HW beyond invocations and will therefore
   # reset their respective settings as it's not possible to read back
   # from the chip.
   # In fact the same is true of a program restart so only use relative
   # adjust functions (_up / _down / etc) if your program stays running!
   volume=30
   balance=0
   bass=0
   treble=0
   def __init__(self):

      self.sc7314_device = i2c_device(ADDRESS)

      self.cmd(SET_AUDIO_SW | INPUT_1 | LOUDNESS_OFF | GAIN_0)
      self.set_balance(0)
      sleep(0.2)
   
   def cmd(self, cmd):
      self.sc7314_device.write_cmd(cmd)

   def set_volume(self, set_volume):
      # The binary version of a number from 0-63 is the bitwise inverse of the volume bits
      # Therefore subtract it from 00111111 (0x3F) or the same as VOL_00|VOL_01 defined above
      # and this makes the correct volume bits for the chip. Now call this with volume=[0...63]
      self.volume=set_volume
      self.cmd(SET_VOLUME | (VOL_00|VOL_01)-set_volume)

   def volume_up(self, increment=1):
      if increment>63: increment=63
      if increment<1: increment=1
      self.volume=self.volume+increment
      if self.volume > 63: self.volume=63
      
      self.set_volume(self.volume)

   def volume_down(self, increment=1):
      if increment>63: increment=63
      if increment<1: increment=1
      self.volume=self.volume-increment
      if self.volume < 0: self.volume=0
      self.set_volume(self.volume)

   def set_input(self, ainput):
      if ainput == 1:
         inputbits=INPUT_1
      if ainput == 2:
         inputbits=INPUT_2
      if ainput == 3:
         inputbits=INPUT_3
      if ainput == 4:
         inputbits=INPUT_4
      self.cmd(SET_AUDIO_SW | inputbits)

   def set_gain(self, set_gain):
       if set_gain==1: self.cmd(SET_AUDIO_SW | GAIN_0)
       if set_gain==2: self.cmd(SET_AUDIO_SW | GAIN_1)
       if set_gain==3: self.cmd(SET_AUDIO_SW | GAIN_2)
       if set_gain==4: self.cmd(SET_AUDIO_SW | GAIN_3)

   def set_balance(self, set_balance):
      att_left=0
      att_right=0

      if (set_balance > -32 and set_balance < 32):
         self.balance=set_balance

      if (set_balance > -32 and set_balance < 0):
          att_left=0
          att_right=-1*(set_balance)
          
      if (set_balance > 0 and set_balance < 32):
          att_left=1*(set_balance)
          att_right=0

      self.cmd(SET_SPK_ATT_L | att_left)
      self.cmd(SET_SPK_ATT_R | att_right)

   def set_balance_l(self, increment=1):
      if increment>31: increment=31
      if increment<1: increment=1
      self.balance=self.balance-increment
      if self.balance < -31: self.balance=-31
      self.set_balance(self.balance)

   def set_balance_r(self, increment=1):
      if increment>31: increment=31
      if increment<1: increment=1
      self.balance=self.balance+increment
      if self.balance > 31: self.balance=31
      self.set_balance(self.balance)

   def set_bass(self, set_bass):
      # Bass goes 0-7,15-8 (-14dB-0dB,0dB-14dB)
      if (set_bass > -8 and set_bass < 8):
         self.bass=set_bass
      if set_bass>=0:
         self.cmd(SET_BASS_CTRL | 15-set_bass)
      if set_bass<0:
         self.cmd(SET_BASS_CTRL | 7-(-1*set_bass))


   def set_bass_down(self, increment=1):
      if increment>7: increment=7
      if increment<1: increment=1
      self.bass=self.bass-increment
      if self.bass < -7: self.bass=-7
      self.set_bass(self.bass)

   def set_bass_up(self, increment=1):
      if increment>6: increment=7
      if increment<1: increment=1
      self.bass=self.bass+increment
      if self.bass > 7: self.bass=7
      self.set_bass(self.bass)

   def set_treble(self, set_treble):
      # Bass goes 0-7,15-8 (-14dB-0dB,0dB-14dB)
      if (set_treble > -8 and set_treble < 8):
         self.treble=set_treble
                
      self.cmd(SET_TREBLE_CTRL | (set_treble+7))

   def set_treble(self, set_treble):
      if (set_treble > -8 and set_treble < 8):
         self.treble=set_treble
                
      if set_treble>=0:
         self.cmd(SET_TREBLE_CTRL | 15-set_treble)
      if set_treble<0:
         self.cmd(SET_TREBLE_CTRL | 7-(-1*set_treble))

   def set_treble_down(self, increment=1):
      if increment>7: increment=7
      if increment<1: increment=1
      self.treble=self.treble-increment
      if self.treble < -7: self.treble=-7
      self.set_treble(self.treble)

   def set_treble_up(self, increment=1):
      if increment>6: increment=7
      if increment<1: increment=1
      self.treble=self.treble+increment
      if self.treble > 7: self.treble=7
      self.set_treble(self.treble)
