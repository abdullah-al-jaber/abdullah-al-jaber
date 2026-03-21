# ==============================
# Variables
# ==============================
CUSTOM_TAG="LEGEND NEVER DIES"

# ==============================
# Functions
# ==============================
echo_lines() {
	echo
	for line in "$@"; do
		echo "$line"
	done
	echo
}

write_lines() {
	local file="$1" && shift
	local lines=("$@")

	if ! grep -qF "$CUSTOM_TAG" "$file" 2>/dev/null; then
		echo_lines "# $CUSTOM_TAG #" "${lines[@]}" >>"$file"
	fi
}

# ==============================
# Main Execution
# ==============================
termux-change-repo
yes | pkg upgrade
yes | pkg install proot-distro fish starship

curl -L https://raw.githubusercontent.com/adi1090x/termux-style/refs/heads/master/colors/smyck.properties -o ~/.termux/colors.properties
curl -L https://raw.githubusercontent.com/ryanoasis/nerd-fonts/refs/heads/master/patched-fonts/FiraCode/Regular/FiraCodeNerdFont-Regular.ttf -o ~/.termux/font.ttf
write_lines ~/.termux/termux.properties \
	'disable-terminal-session-change-toast = true' \
	'terminal-transcript-rows = 5000' \
	'volume-keys = volume' \
	'use-black-ui = true' \
	'bell-character = ignore' \
	'terminal-margin-horizontal=5' \
	'terminal-margin-vertical=5'
mv ~/../usr/etc/motd ~/../usr/etc/motd.bk 2>/dev/null

proot-distro install fedora
proot-distro clear-cache

chsh -s fish
echo_lines \
	'alias --save fedora="proot-distro login fedora --bind /storage/emulated/0/:/android --isolated"' \
	'alias --save clear-history="yes yes | history clear"' \
	'set -U fish_greeting' |
	fish
write_lines ~/.config/fish/config.fish \
	'starship init fish | source'
starship preset bracketed-segments -o ~/.config/starship.toml
sed -i '9,11d' ~/.config/starship.toml
sed -i '2i scan_timeout = 0' ~/.config/starship.toml
write_lines ~/.config/starship.toml \
	'[character]' \
	'disabled = false' \
	'error_symbol = "[❯](red)"' \
	'success_symbol = "[❯](blue)"'

history -c && history -w
exit
