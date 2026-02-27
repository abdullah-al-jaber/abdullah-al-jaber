# source <(curl -sSL https://raw.githubusercontent.com/abdullah-al-jaber/abdullah-al-jaber/vanilla/shell-script/fedora.sh)
rm -f /etc/yum.repos.d/fedora-cisco-openh264.repo
dnf upgrade -y
dnf install -y nodejs npm python pip fish openssl nano neovim glibc-langpack-en ncurses wget
useradd -m -p "$(openssl passwd -6 123)" retro-boy
echo "retro-boy ALL=(ALL) ALL" >>/etc/sudoers
cat <<'EOF' >>/root/.bashrc
if [ "$(id -u)" -eq 0 ] && [ "$SUDO_USER" = "" ]; then
  exec su - retro-boy
fi
EOF
cat <<'EOF' >>~/.bash_profile
if [ -f ~/.bashrc ]; then
  source ~/.bashrc
fi
EOF
chsh -s /usr/bin/fish retro-boy
sudo -u retro-boy fish -c "set -U fish_greeting"
sudo -u retro-boy fish -c "set -Ux LANG en_US.UTF-8"
sudo -u retro-boy fish -c "alias --save clear-history='yes yes | history clear'"
dnf copr enable atim/starship -y
dnf install -y starship
sudo -u retro-boy sh -c "echo 'starship init fish | source' >> ~/.config/fish/config.fish"
sudo -u retro-boy sh -c "starship preset bracketed-segments -o ~/.config/starship.toml"
sudo -u retro-boy sh -c "sed -i '2i scan_timeout = 0' ~/.config/starship.toml"
history -c && >~/.bash_history && history -w
exit
