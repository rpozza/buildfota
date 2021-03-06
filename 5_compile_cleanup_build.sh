#!/bin/bash

#Remapping Flash scatter, building and making SECONDARY BOOT LOADER
cp ../deskegg/SDK/libraries/mbed/targets/cmsis/TARGET_NXP/TARGET_LPC176X/cmsis_nvic.sblignore ../deskegg/SDK/libraries/mbed/targets/cmsis/TARGET_NXP/TARGET_LPC176X/cmsis_nvic.c
cp ../deskegg/SDK/libraries/mbed/targets/cmsis/TARGET_NXP/TARGET_LPC176X/TOOLCHAIN_GCC_ARM/LPC1768.sblignore ../deskegg/SDK/libraries/mbed/targets/cmsis/TARGET_NXP/TARGET_LPC176X/TOOLCHAIN_GCC_ARM/LPC1768.ld
../deskegg/SDK/workspace_tools/build.py -"mARCH_PRO" -"tGCC_ARM" -"c" -"v" -"r" -"x"
../deskegg/SDK/workspace_tools/make.py -"mARCH_PRO" -"tGCC_ARM" -"p137" -"v" -"c" -"DMAGIC_CODE=\"0\"" -"DLWM2M_CLIENTNAME=\"NO\"" -"DLWM2M_WIFI_SSID=\"NO\"" -"DLWM2M_WIFI_PSWD=\"NO\"" -"DSBL_CLEAN_BUILD"
cp ../deskegg/SDK/build/test/ARCH_PRO/GCC_ARM/SBL/sbl.bin .

mv sbl.bin cleanup.bin
