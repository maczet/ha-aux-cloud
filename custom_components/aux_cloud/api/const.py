from enum import IntFlag, StrEnum, auto

# Used to fetch params from the device that are not returned in basic call
AUX_MODEL_TO_PARAMS = {
  "000000000000000000000000c0620000": [
    'mode'
  ],
  "000000000000000000000000c3aa0000": [
    'hp_water_tank_temp'
  ]
}

AUX_MODEL_TO_NAME = {
    "000000000000000000000000c3aa0000": "AUX Heat Pump",
    "000000000000000000000000c0620000": "AUX Air Conditioner",
}

AC = "Air Conditioner"
HEAT_PUMP = "Heat Pump"

class AUX_PRODUCT_CATEGORY(auto):
  HEAT_PUMP = [
    "000000000000000000000000c3aa0000"
  ]

  AC = [
    "000000000000000000000000c0620000"
  ]


POWER_OFF: dict = {"pwr": 0}
POWER_ON: dict = {"pwr": 1}
HEATING: dict = {"ac_mode": 1}
COOLING: dict = {"ac_mode": 0}
FAN_SPEEDS_LOW: dict = {"ac_mark": 1}
FAN_SPEEDS_HIGH: dict = {"ac_mark": 4}

# TODO need to be refactored
TEMP: dict = {"temp": 240}


"""
AC PARAMETERS NOT TESTED ALL
'ac_astheat': 0 - Auxiliary heating is off
'ac_clean': 0 - Self-cleaning function is off
'ac_errcode1': 0 - No error code (system functioning normally)
'ac_hdir': 0 - Horizontal airflow direction at default/center position
'ac_health': 0 - Health function (likely ionizer/purifier) is off
'ac_mark': 1 - Fan speed 1 is lowest speed (typical speeds: 1=Low, 2=Medium, 3=High, 4=Turbo, 5=Mute)
'ac_mode': 1 - Mode is set to 1, likely "Cool" mode (typical modes: 0=Auto, 1=Cool, 2=Dry, 3=Fan, 4=Heat)
'ac_slp': 0 - Sleep mode is off
'ac_tempconvert': 0 - No temperature conversion happening
'ac_vdir': 0 - Vertical airflow direction at default/center position
'childlock': 0 - Child lock feature is off
'comfwind': 0 - Comfortable wind mode is off
'ecomode': 0 - Economy/energy-saving mode is off
'envtemp': 236 - Current environment/room temperature (likely 23.6°C)
'err_flag': 0 - No error flag
'mldprf': 0 - Mildew proof/prevention function is off
'model': 1 - Device model identifier
'new_type': 1 - Indicates this is a newer type of AC unit
'pwr': 0 - Power is off (unit is in standby)
'pwrlimit': 0 - Power limitation function is off
'pwrlimitswitch': 0 - Power limit switch is off
'scrdisp': 1 - Screen display is on
'sleepdiy': 1 - Custom sleep mode is on
'temp': 240 - Set temperature (likely 24.0°C)
'tempunit': 1 - Temperature unit (1 typically means Celsius)

HEAT PUMP PARAMETERS NOT TESTED
'hp_pwr'
'hp_water_tank_temp'
'ac_errcode1'
'hp_fast_hotwater'
'err_flag'
'hp_auto_wtemp'
'ac_pwr'
'hp_hotwater_temp'
'ac_temp'
'ac_mode'
'qtmode'
'ecomode'
'ver_old'
"""