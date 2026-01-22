cd ~
termux-change-repo
yes | pkg upgrade
mv ../usr/etc/motd ../usr/etc/motd.bk
pkg install -y proot-distro
proot-distro install fedora
proot-distro clear-cache
echo -e "\n"
curl -L https://example.com/file.zip -o file.zip
unzip file.zip
rm file.zip
