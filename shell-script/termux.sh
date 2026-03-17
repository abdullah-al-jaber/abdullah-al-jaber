# source <(curl -sSL https://raw.githubusercontent.com/abdullah-al-jaber/abdullah-al-jaber/vanilla/shell-script/termux.sh)
cd ~
termux-change-repo
yes | pkg upgrade
mv ../usr/etc/motd ../usr/etc/motd.bk
pkg install -y proot-distro fish starship
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
	-e 's/^# terminal-margin-vertical=0$/terminal-margin-vertical=5/' \
	.termux/termux.properties
chsh -s fish
fish -c 'alias --save fedora="proot-distro login fedora --bind /storage/emulated/0/:/android --isolated"'
fish -c 'alias --save clear-history="yes yes | history clear"'
fish -c 'set -U fish_greeting'
echo 'starship init fish | source' >>~/.config/fish/config.fish
starship preset bracketed-segments -o ~/.config/starship.toml
sed -i '9,11d' ~/.config/starship.toml
sed -i '2i scan_timeout = 0' ~/.config/starship.toml
history -c && >~/.bash_history && history -w
exit
