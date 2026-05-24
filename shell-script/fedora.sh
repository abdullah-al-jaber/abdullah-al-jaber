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
dnf copr enable atim/starship -y
dnf upgrade -y
dnf install nodejs npm python pip nano neovim fish starship openssl glibc-langpack-en ncurses util-linux -y

useradd -m -p "$(openssl passwd -6 123)" retro-boy
write_lines /etc/sudoers \
	'retro-boy   ALL=(ALL)   ALL'
write_lines ~/.bashrc \
	'if [ "$(id -u)" -eq 0 ] && [ "$SUDO_USER" = "" ]; then' \
	'  exec su - retro-boy' \
	'fi'
write_lines ~/.bash_profile \
	'if [ -f ~/.bashrc ]; then' \
	'  source ~/.bashrc' \
	'fi'

chsh -s /usr/bin/fish retro-boy
echo_lines \
	'set -U fish_greeting' \
	'set -Ux LANG en_US.UTF-8' \
	'alias --save clear-history="yes yes | history clear"' \
	'echo "starship init fish | source" >> ~/.config/fish/config.fish' \
	'starship preset bracketed-segments -o ~/.config/starship.toml' \
	'sed -i "2i scan_timeout = 0" ~/.config/starship.toml' |
	sudo -u retro-boy fish

history -c && history -w
exit
