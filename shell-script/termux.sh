# source <(curl -sSL https://raw.githubusercontent.com/abdullah-al-jaber/abdullah-al-jaber/vanilla/shell-script/termux.sh)
cd ~
termux-change-repo
yes | pkg upgrade
mv ../usr/etc/motd ../usr/etc/motd.bk
pkg install -y proot-distro
proot-distro install fedora
proot-distro clear-cache
curl -L https://raw.githubusercontent.com/adi1090x/termux-style/refs/heads/master/colors/smyck.properties -o .termux/colors.properties
curl -L https://raw.githubusercontent.com/ryanoasis/nerd-fonts/refs/heads/master/patched-fonts/FiraCode/Regular/FiraCodeNerdFont-Regular.ttf -o .termux/font.ttf
sed -i \
	-e 's/^# disable-terminal-session-change-toast = true$/disable-terminal-session-change-toast = true/' \
	-e 's/^# terminal-transcript-rows = 2000$/terminal-transcript-rows = 5000/' \
	-e 's/^# volume-keys = volume$/volume-keys = volume/' \
	-e 's/^# use-black-ui = true$/use-black-ui = true/' \
	-e 's/^# bell-character = ignore$/bell-character = ignore/' \
	-e 's/^# terminal-margin-horizontal=3$/terminal-margin-horizontal=5/' \
	-e 's/^# terminal-margin-vertical=0$/terminal-margin-vertical=10/' \
	.termux/termux.properties
cat <<'EOF' >>~/.bashrc
alias fedora='proot-distro login fedora --bind /sdcard:/android --isolated'
alias clear-history='history -c && history -w'
fedora
EOF
history -c && >~/.bash_history && history -w
exit
