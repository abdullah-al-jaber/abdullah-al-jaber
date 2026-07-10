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
dnf upgrade -y
dnf install fish eza -y

chown root:root /usr/bin/sudo
chmod 4755 /usr/bin/sudo

useradd -m -p "$(openssl passwd -6 123)" retro-boy
write_lines /etc/sudoers \
	'retro-boy   ALL=(ALL)   ALL'

chsh -s /usr/bin/fish retro-boy
echo_lines \
	'alias --save clear-history="echo yes | history clear"' \
	'alias lz="eza --icons --sort=type"' \
	'echo y | fish_config prompt save scales' \
	'set -Ux LANG en_US.UTF-8'\
	'set -U fish_greeting'  |
	sudo -u retro-boy fish

history -c && history -w
exit
