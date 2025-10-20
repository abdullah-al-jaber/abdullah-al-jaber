#!/data/data/com.termux/files/usr/bin/sh
pkg update && yes || pkg upgrade
cd $HOME
git clone https://github.com/adi1090x/termux-style
cd termux-style
./install