# source <(curl -sSL https://raw.githubusercontent.com/abdullah-al-jaber/abdullah-al-jaber/vanilla/shell-script/fedora.sh)
dnf upgrade -y
dnf copr enable alternateved/eza
dnf install -y nodejs npm python pip zsh openssl nano neovim glibc-langpack-en ncurses wget eza
useradd -m -p '$(openssl passwd -6 123)' retro-boy
echo 'retro-boy ALL=(ALL) ALL' >> /etc/sudoers
cat <<'EOF' >>~/.bashrc
if [ '$(id -u)' -eq 0 ] && [ '$SUDO_USER' = '' ]; then
  exec su - retro-boy
fi
EOF
cat <<'EOF' >> ~/.bash_profile
if [ -f ~/.bashrc ]; then
  source ~/.bashrc
fi
EOF
sudo -u retro-boy zsh -c 'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended'
sudo -u retro-boy zsh -c 'git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting'
sudo -u retro-boy zsh -c 'git clone https://github.com/marlonrichert/zsh-autocomplete.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autocomplete'
sudo -u retro-boy zsh -c 'git clone https://github.com/z-shell/zsh-eza.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-eza'
chsh -s /usr/bin/zsh retro-boy
sudo -u retro-boy zsh -c 'sed -i "s/plugins=(git)/plugins=(git zsh-syntax-highlighting zsh-autocomplete zsh-eza)/g" ~/.zshrc'
cat <<'EOF' >> /home/retro-boy/.zshrc
alias clear-history='yes | history -c'
EOF
history -c && >~/.bash_history && history -w
exit
