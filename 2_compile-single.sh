#!/bin/bash

if [ $# -ne 6 ]; then 
   echo "Usage: $0 client_name hostname psk_id psk_pwd wifi_ssid wifi_pwd"
   echo " "
   echo "Example: $0 mylwmwmclient myserver client_id client_pswd my_wifi 1234"
   echo " "	   
   exit
fi


#Remapping Flash scatter, building and making SECONDARY BOOT LOADER
cp ../deskegg/SDK/libraries/mbed/targets/cmsis/TARGET_NXP/TARGET_LPC176X/cmsis_nvic.sblignore ../deskegg/SDK/libraries/mbed/targets/cmsis/TARGET_NXP/TARGET_LPC176X/cmsis_nvic.c
cp ../deskegg/SDK/libraries/mbed/targets/cmsis/TARGET_NXP/TARGET_LPC176X/TOOLCHAIN_GCC_ARM/LPC1768.sblignore ../deskegg/SDK/libraries/mbed/targets/cmsis/TARGET_NXP/TARGET_LPC176X/TOOLCHAIN_GCC_ARM/LPC1768.ld
../deskegg/SDK/workspace_tools/build.py -"mARCH_PRO" -"tGCC_ARM" -"c" -"v" -"r" -"x"
../deskegg/SDK/workspace_tools/make.py -"mARCH_PRO" -"tGCC_ARM" -"p137" -"v" -"c"
cp ../deskegg/SDK/build/test/ARCH_PRO/GCC_ARM/SBL/sbl.bin .

#Remapping Flash scatter, building and making Wakaama FW
cp ../deskegg/SDK/libraries/mbed/targets/cmsis/TARGET_NXP/TARGET_LPC176X/cmsis_nvic.eggignore ../deskegg/SDK/libraries/mbed/targets/cmsis/TARGET_NXP/TARGET_LPC176X/cmsis_nvic.c
cp ../deskegg/SDK/libraries/mbed/targets/cmsis/TARGET_NXP/TARGET_LPC176X/TOOLCHAIN_GCC_ARM/LPC1768.eggignore ../deskegg/SDK/libraries/mbed/targets/cmsis/TARGET_NXP/TARGET_LPC176X/TOOLCHAIN_GCC_ARM/LPC1768.ld
../deskegg/SDK/workspace_tools/build.py -"mARCH_PRO" -"tGCC_ARM" -"c" -"v" -"r" -"x"
../deskegg/SDK/workspace_tools/make.py -"mARCH_PRO" -"tGCC_ARM" -"p135" -"v" -"c" -"DLWM2M_LITTLE_ENDIAN" -"DLWM2M_CLIENT_MODE" -"DWITH_TINYDTLS" -"DWITH_SHA256" -"DLWM2M_CLIENTNAME=\"$1\"" -"DLWM2M_SERVER_HOSTNAME=\"$2\"" -"DLWM2M_PRESHAREDKEY_CLIENTID=\"$3\"" -"DLWM2M_PRESHAREDKEY_CLIENTPSWD=\"$4\"" -"DLWM2M_WIFI_SSID=\"$5\"" -"DLWM2M_WIFI_PSWD=\"$6\""
cp ../deskegg/SDK/build/test/ARCH_PRO/GCC_ARM/WakaamaDTLS/client.bin .

#Generating Blank 64K image
dd if=/dev/zero ibs=1k count=64 | tr "\000" "\377" > blank64k.bin
dd if=sbl.bin of=blank64k.bin conv=notrunc
cat blank64k.bin client.bin > $1.bin
rm client.bin
rm blank64k.bin
rm sbl.bin
