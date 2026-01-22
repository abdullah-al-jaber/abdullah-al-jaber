# source <(curl -sSL https://raw.githubusercontent.com/abdullah-al-jaber/abdullah-al-jaber/vanilla/shell-script/fedora.sh)
rm /etc/yum.repos.d/fedora-cisco-openh264.repo
dnf upgrade -y
dnf install -y nodejs python pip fish openssl nano neovim
useradd -m -p "$(openssl passwd -6 123)" retro-boy
echo "retro-boy ALL=(ALL) ALL" >> /etc/sudoers
cat <<'EOF' >> /root/.bashrc
if [ "$(id -u)" -eq 0 ] && [ "$SUDO_USER" = "" ]; then
  exec su - retro-boy
fi
EOF
cat <<'EOF'>> ~/.bash_profile
if [ -f ~/.bashrc ]; then
  source ~/.bashrc
fi
EOF
sudo -u retro-boy sh -c "chsh -s /usr/bin/fish"
sudo -u retro-boy sh -c "fish -c 'set -U fish_greeting'"
dnf copr enable atim/starship -y
dnf install -y starship
sudo -u retro-boy "echo 'starship init fish | source' >> ~/.config/fish/config.fish"
sudo -u retro-boy "starship preset bracketed-segments -o ~/.config/starship.toml"
history -c && > ~/.bash_history && history -w
exit
