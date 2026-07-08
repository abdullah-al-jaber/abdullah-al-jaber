set -eE
trap 'echo -e "ERROR —⟩ $BASH_COMMAND [$LINENO]"; read -p "[PRESS ENTER TO EXIT]"' ERR

sudo dnf install gh git -y
yes | gh auth login --git-protocol https --scopes repo,codespace --web
gh auth setup-git
git config --global --add safe.directory '/mnt/sdcard/PlayGround/*'


