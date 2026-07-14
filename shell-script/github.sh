set -eE
trap 'echo -e "ERROR —⟩ $BASH_COMMAND [$LINENO]"; read -p "[PRESS ENTER TO EXIT]"' ERR

for cmd in gh git; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "DEPENDENCY FAILURE —⟩ gh git"
        exit 1
    fi
done

echo y | gh auth login --git-protocol https --scopes repo,codespace --web && gh auth setup-git
git config --global --add safe.directory '/sdcard/PlayGround/*'
git config --global --add safe.directory '/android/PlayGround/*'
git config --global user.email 'abdullah.0.al.0.jaber@gmail.com'
git config --global user.name 'Abdullah Al Jaber'
