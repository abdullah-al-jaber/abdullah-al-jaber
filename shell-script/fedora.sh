# source <(curl -sSL https://raw.githubusercontent.com/abdullah-al-jaber/abdullah-al-jaber/vanilla/shell-script/fedora.sh)
dnf upgrade -y
dnf copr -y enable alternateved/eza
dnf copr -y enable atim/starship
dnf install -y nodejs npm python pip zsh openssl nano neovim glibc-langpack-en ncurses wget eza git starship
useradd -m -p "$(openssl passwd -6 123)" retro-boy
echo 'retro-boy ALL=(ALL) ALL' >>/etc/sudoers
cat <<'EOF' >>~/.bashrc
if [ "$(id -u)" -eq 0 ] && [ "$SUDO_USER" = "" ]; then
  exec su - retro-boy
fi
EOF
cat <<'EOF' >>~/.bash_profile
if [ -f ~/.bashrc ]; then
  source ~/.bashrc
fi
EOF
sudo -u retro-boy zsh -c 'yes n | bash -c "$(curl --fail --show-error --silent --location https://raw.githubusercontent.com/zdharma-continuum/zinit/HEAD/scripts/install.sh)"'
sudo -u retro-boy zsh -c 'echo "ZSH_AUTOSUGGEST_STRATEGY=(history completion)" >>~/.zshrc'
sudo -u retro-boy zsh -c 'echo "zinit ice lucid" >>~/.zshrc'
sudo -u retro-boy zsh -c 'echo "zinit light zsh-users/zsh-autosuggestions" >>~/.zshrc'
sudo -u retro-boy zsh -c 'echo "zinit ice lucid" >>~/.zshrc'
sudo -u retro-boy zsh -c 'echo "zinit light zsh-users/zsh-syntax-highlighting" >>~/.zshrc'
sudo -u retro-boy zsh -c 'echo "zinit ice lucid" >>~/.zshrc'
sudo -u retro-boy zsh -c 'echo "zinit light z-shell/zsh-eza" >>~/.zshrc'
sudo -u retro-boy zsh -c 'echo "eval \"\$(starship init zsh)\"" >>~/.zshrc'
sudo -u retro-boy zsh -c 'echo "alias clear-history=\"history -p\"" >>~/.zshrc'
sudo -u retro-boy zsh -c 'starship preset bracketed-segments -o ~/.config/starship.toml'
chsh -s /usr/bin/zsh retro-boy
history -c && >~/.bash_history && history -w
exit
