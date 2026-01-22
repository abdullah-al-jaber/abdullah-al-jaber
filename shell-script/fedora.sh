# source <(curl -sSL https://raw.githubusercontent.com/abdullah-al-jaber/abdullah-al-jaber/vanilla/shell-script/fedora.sh)
rm /etc/yum.repos.d/fedora-cisco-openh264.repo
dnf upgrade -y
dnf install -y nodejs python pip fish openssl
useradd -m -p "$(openssl passwd -6 123)" retro-boy
echo "retro-boy ALL=(ALL) ALL" >> /etc/sudoers
cat <<'EOF' >> /root/.bashrc
if [ "$(id -u)" -eq 0 ] && [ "$SUDO_USER" = "" ]; then
  exec su - retro-boy
fi
EOF
exit 
