cd ~
termux-change-repo
yes | pkg upgrade
mv ../usr/etc/motd ../usr/etc/motd.bk
pkg install -y proot-distro
proot-distro install fedora
proot-distro clear-cache
curl -L https://abdullah-al-jaber.github.io/asset/archive/termux.zip -o termux.zip
unzip -o termux.zip
rm termux.zip
kill -9 $PPID
