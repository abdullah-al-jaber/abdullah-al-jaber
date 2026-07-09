set -eE
trap 'echo -e "ERROR —⟩ $BASH_COMMAND [$LINENO]"; read -p "[PRESS ENTER TO EXIT]"' ERR

# ==============================
# Variables
# ==============================
CUSTOM_TAG="LEGEND NEVER DIES"

# ==============================
# Functions
# ==============================
echo_lines() {
	for line in "$@"; do
		echo -e "$line"
	done
}

write_lines() {
	local file="$1" && shift
	local lines=("$@")

	if ! grep -qF "$CUSTOM_TAG" "$file" 2>/dev/null; then
		echo_lines "\n" "# $CUSTOM_TAG #" "${lines[@]}" >>"$file"
	fi
}

# ==============================
# Main Execution
# ==============================
termux-change-repo
yes | pkg upgrade
yes | pkg install sudo fish proot-distro 

curl -sSL https://raw.githubusercontent.com/adi1090x/termux-style/refs/heads/master/colors/smyck.properties -o ~/.termux/colors.properties
curl -sSL https://raw.githubusercontent.com/ryanoasis/nerd-fonts/refs/heads/master/patched-fonts/FiraCode/Regular/FiraCodeNerdFont-Regular.ttf -o ~/.termux/font.ttf
write_lines ~/.termux/termux.properties \
	'disable-terminal-session-change-toast = true' \
	'terminal-transcript-rows = 8000' \
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
	'alias --save fedora="proot-distro login fedora --bind /storage/emulated/0/:/android --user retro-boy --isolated"' \
	'alias --save fdr-rt="proot-distro login fedora --bind /storage/emulated/0/:/android --user root --isolated"' \
	'alias --save clear-history="echo yes | history clear"' \
	'echo y | fish_config prompt save arrow' \
	'set -U fish_greeting' |
	fish

history -c && history -w
exit
