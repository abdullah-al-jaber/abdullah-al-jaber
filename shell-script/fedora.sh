# source <(curl -s https://example.com/script.sh)
rm /etc/yum.repos.d/fedora-cisco-openh264.repo
dnf upgrade -y
dnf install -y nodejs python pip fish
useradd -m -p "$(openssl passwd -6 yourpass)" retro-boy
echo "retro-boy ALL=(ALL) ALL" >> /etc/sudoers
cat <<'EOF' >> /root/.bashrc
if [ "$(id -u)" -eq 0 ] && [ "$SUDO_USER" = "" ]; then
  exec su - retro-boy
fi
EOF
exit 