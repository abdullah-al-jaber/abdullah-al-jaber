# source <(curl -sSL https://raw.githubusercontent.com/abdullah-al-jaber/abdullah-al-jaber/vanilla/shell-script/termux.sh)

# FUNCTIONS
echo_lines() {
	local text=""
	local flag=1
	for line in "$@"; do
		if [ "$flag" -eq 1 ]; then
			text="$line"
			flag=0
		else
			text+="\n$line"
		fi
	done
	echo -e "\n$text\n"
}

# PACKAGE
termux-change-repo
yes | pkg upgrade
yes | pkg install proot-distro fish starship
mv ~/../usr/etc/motd ~/../usr/etc/motd.bk

# PROOT
proot-distro install fedora
proot-distro clear-cache

# TERMUX
curl -L https://raw.githubusercontent.com/adi1090x/termux-style/refs/heads/master/colors/smyck.properties -o .termux/colors.properties
curl -L https://raw.githubusercontent.com/ryanoasis/nerd-fonts/refs/heads/master/patched-fonts/FiraCode/Regular/FiraCodeNerdFont-Regular.ttf -o .termux/font.ttf
echo_lines \
	"# CUSTOM CONFIG #" \
	"disable-terminal-session-change-toast = true" \
	"terminal-transcript-rows = 5000" \
	"volume-keys = volume" \
	"use-black-ui = true" \
	"bell-character = ignore" \
	"terminal-margin-horizontal=5" \
	"terminal-margin-vertical=5" \
	>>~/.termux/termux.properties

# SHELL
chsh -s fish
echo_lines \
	'alias --save fedora="proot-distro login fedora --bind /storage/emulated/0/:/android --isolated"' \
	'alias --save clear-history="yes yes | history clear"' \
	'set -U fish_greeting' |
	fish
echo 'starship init fish | source' >>~/.config/fish/config.fish
starship preset bracketed-segments -o ~/.config/starship.toml
sed -i '9,11d' ~/.config/starship.toml
sed -i '2i scan_timeout = 0' ~/.config/starship.toml
echo_lines \
	'# CUSTOM CONFIG #' \
	'[character]' \
	'disabled = false' \
	'error_symbol = "[❯](red)"' \
	'success_symbol = "[❯](blue)"' \
	>>~/.config/starship.toml
history -c && >~/.bash_history && history -w
exit
