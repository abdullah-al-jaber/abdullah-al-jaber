sudo dnf install gh git -y
yes | gh auth login --git-protocol https --scopes repo,codespace --web
git config --global --add safe.directory '/mnt/sdcard/PlayGround/*'
git config --global user.email 'abdullah.0.al.0.jaber@gmail.com'
git config --global user.name 'Abdullah Al Jaber'