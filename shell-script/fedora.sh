# source <(curl -sSL https://raw.githubusercontent.com/abdullah-al-jaber/abdullah-al-jaber/vanilla/shell-script/fedora.sh)

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
yes | dnf copr enable atim/starship
yes | dnf upgrade
yes | dnf install nodejs npm python pip nano neovim fish starship openssl glibc-langpack-en ncurses

# USER
useradd -m -p "$(openssl passwd -6 123)" retro-boy
echo_lines \
	'# CUSTOM CONFIG #' \
	'retro-boy   ALL=(ALL)   ALL' \
	>>/etc/sudoers
echo_lines \
	'# CUSTOM CONFIG #' \
	'if [ "$(id -u)" -eq 0 ] && [ "$SUDO_USER" = "" ]; then' \
	'  exec su - retro-boy' \
	'fi' \
	>>~/.bashrc
echo_lines \
	'# CUSTOM CONFIG #' \
	'if [ -f ~/.bashrc ]; then' \
	'  source ~/.bashrc' \
	'fi' \
	>>~/.bash_profile

# SHELL
chsh -s /usr/bin/fish retro-boy
echo_lines \
	'set -U fish_greeting' \
	'set -Ux LANG en_US.UTF-8' \
	'alias --save clear-history="yes yes | history clear"' \
	'echo "starship init fish | source" >> ~/.config/fish/config.fish' \
	'starship preset bracketed-segments -o ~/.config/starship.toml' \
	'sed -i "2i scan_timeout = 0" ~/.config/starship.toml' |
	sudo -u retro-boy fish
history -c && >~/.bash_history && history -w
exit
