#!/bin/bash

LOGO=res/icons/logo
ICONS=()
# sudo apt-get install inkscape
for sz in 16 24 32 48 256 ; do
	inkscape -w $sz -h $sz -e "${LOGO}_${sz}.png" "${LOGO}.svg"
	ICONS=("${ICONS[@]}" "${LOGO}_${sz}.png")
done
# sudo apt-get install imagemagick
convert "${ICONS[@]}" "${LOGO}.ico"

identify "${LOGO}.ico"