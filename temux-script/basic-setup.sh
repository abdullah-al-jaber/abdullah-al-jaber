#!/data/data/com.termux/files/usr/bin/sh
termux-change-repo
pkg update
yes | pkg upgrade
mv /data/data/com.termux/files/usr/etc/motd /data/data/com.termux/files/usr/etc/.motd

cd $HOME
git clone https://github.com/adi1090x/termux-style
cd termux-style
./install

pkg install fish
chsh -s fish
fish -c "set -U fish_greeting ' '"
fish -c "fish_config prompt choose scales"
fish -c "yes | fish_config prompt save"
exit
