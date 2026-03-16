# source <(curl -sSL https://raw.githubusercontent.com/abdullah-al-jaber/abdullah-al-jaber/vanilla/shell-script/fedora.sh)
dnf upgrade -y
dnf copr -y enable alternateved/eza
dnf install -y nodejs npm python pip zsh openssl nano neovim glibc-langpack-en ncurses wget eza git
useradd -m -p "$(openssl passwd -6 123)" retro-boy
echo 'retro-boy ALL=(ALL) ALL' >> /etc/sudoers
cat <<'EOF' >> ~/.bashrc
if [ "$(id -u)" -eq 0 ] && [ "$SUDO_USER" = "" ]; then
  exec su - retro-boy
fi
EOF
cat <<'EOF' >> ~/.bash_profile
if [ -f ~/.bashrc ]; then
  source ~/.bashrc
fi
EOF
sudo -u retro-boy zsh 'yes n | bash -c "$(curl --fail --show-error --silent --location https://raw.githubusercontent.com/zdharma-continuum/zinit/HEAD/scripts/install.sh)"'
sudo -u retro-boy zsh -c 'echo "zinit light zdharma-continuum/fast-syntax-highlighting" >> ~/.zshrc'
chsh -s /usr/bin/zsh retro-boy
cat <<'EOF' >> /home/retro-boy/.zshrc
alias clear-history='yes | history -c'
EOF
history -c && >~/.bash_history && history -w
exit
