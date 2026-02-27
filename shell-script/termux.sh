# source <(curl -sSL https://raw.githubusercontent.com/abdullah-al-jaber/abdullah-al-jaber/vanilla/shell-script/termux.sh)
cd ~
termux-change-repo
yes | pkg upgrade
mv ../usr/etc/motd ../usr/etc/motd.bk
pkg install -y proot-distro fish starship
proot-distro install fedora
proot-distro clear-cache
curl -L https://raw.githubusercontent.com/adi1090x/termux-style/refs/heads/master/colors/smyck.properties -o .termux/colors.properties
curl -L https://raw.githubusercontent.com/ryanoasis/nerd-fonts/refs/heads/master/patched-fonts/FiraCode/Regular/FiraCodeNerdFont-Regular.ttf -o .termux/font.ttf
sed -i \
	-e 's/^# disable-terminal-session-change-toast = true$/disable-terminal-session-change-toast = true/' \
	-e 's/^# terminal-transcript-rows = 2000$/terminal-transcript-rows = 5000/' \
	-e 's/^# volume-keys = volume$/volume-keys = volume/' \
	-e 's/^# use-black-ui = true$/use-black-ui = true/' \
	-e 's/^# bell-character = ignore$/bell-character = ignore/' \
	-e 's/^# terminal-margin-horizontal=3$/terminal-margin-horizontal=5/' \
	-e 's/^# terminal-margin-vertical=0$/terminal-margin-vertical=5/' \
	.termux/termux.properties
chsh -s fish
fish -c "alias --save fedora='proot-distro login fedora --bind /sdcard:/android --isolated'"
fish -c "alias --save clear-history='yes yes | history clear'"
fish -c "set -U fish_greeting"
echo >> ~/.config/fish/config.fish
echo "starship init fish | source" >> ~/.config/fish/config.fish
cat <<'EOF' >>~/.config/starship.toml
"$schema" = 'https://starship.rs/config-schema.json'
scan_timeout = 0

[aws]
format = '\[[$symbol($profile)(\($region\))(\[$duration\])]($style)\]'

[azure]
format = '\[[$symbol($subscription)]($style)\]'

[buf]
format = '\[[$symbol($version)]($style)\]'

[bun]
format = '\[[$symbol($version)]($style)\]'

[c]
format = '\[[$symbol($version(-$name))]($style)\]'

[character]
disabled = false
success_symbol = '[❯](blue)'
error_symbol = '[❯](red)'

[cmake]
format = '\[[$symbol($version)]($style)\]'

[cmd_duration]
format = '\[[⏱ $duration]($style)\]'

[cobol]
format = '\[[$symbol($version)]($style)\]'

[conda]
format = '\[[$symbol$environment]($style)\]'

[container]
format = '\[[$symbol \[$name\]]($style)\]'

[cpp]
format = '\[[$symbol($version(-$name))]($style)\]'

[crystal]
format = '\[[$symbol($version)]($style)\]'

[daml]
format = '\[[$symbol($version)]($style)\]'

[dart]
format = '\[[$symbol($version)]($style)\]'

[deno]
format = '\[[$symbol($version)]($style)\]'

[direnv]
format = '\[[$symbol$loaded/$allowed]($style)\]'

[docker_context]
format = '\[[$symbol$context]($style)\]'

[dotnet]
format = '\[[$symbol($version)(🎯 $tfm)]($style)\]'

[elixir]
format = '\[[$symbol($version \(OTP $otp_version\))]($style)\]'

[elm]
format = '\[[$symbol($version)]($style)\]'

[erlang]
format = '\[[$symbol($version)]($style)\]'

[fennel]
format = '\[[$symbol($version)]($style)\]'

[fortran]
format = '\[[$symbol($version)]($style)\]'

[fossil_branch]
format = '\[[$symbol$branch]($style)\]'

[fossil_metrics]
format = '\[[+$added]($added_style)\]\[[-$deleted]($deleted_style)\]'

[gcloud]
format = '\[[$symbol$account(@$domain)(\($region\))]($style)\]'

[git_branch]
format = '\[[$symbol$branch]($style)\]'

[git_commit]
format = '\[[\($hash$tag\)]($style)\]'

[git_metrics]
format = '\[[+$added]($added_style)\]\[[-$deleted]($deleted_style)\]'

[git_state]
format = '\[[$state ($progress_current/$progress_total)]($style)\]'

[git_status]
format = '([\[$all_status$ahead_behind\]]($style))'

[gleam]
format = '\[[$symbol($version)]($style)\]'

[golang]
format = '\[[$symbol($version)]($style)\]'

[gradle]
format = '\[[$symbol($version)]($style)\]'

[guix_shell]
format = '\[[$symbol]($style)\]'

[haskell]
format = '\[[$symbol($version)]($style)\]'

[haxe]
format = '\[[$symbol($version)]($style)\]'

[helm]
format = '\[[$symbol($version)]($style)\]'

[hg_branch]
format = '\[[$symbol$branch]($style)\]'

[hostname]
format = '\[[$ssh_symbol($hostname)]($style)\] '

[java]
format = '\[[$symbol($version)]($style)\]'

[jobs]
format = '\[[$symbol$number]($style)\]'

[julia]
format = '\[[$symbol($version)]($style)\]'

[kotlin]
format = '\[[$symbol($version)]($style)\]'

[kubernetes]
format = '\[[$symbol$context( \($namespace\))]($style)\]'

[localip]
format = '\[[$localipv4]($style)\]'

[lua]
format = '\[[$symbol($version)]($style)\]'

[memory_usage]
format = '\[$symbol[$ram( | $swap)]($style)\]'

[meson]
format = '\[[$symbol$project]($style)\]'

[mise]
format = '\[[$symbol$health]($style)\]'

[mojo]
format = '\[[$symbol($version)]($style)\]'

[nats]
format = '\[[$symbol$name]($style)\]'

[netns]
format = '\[[$symbol \[$name\]]($style)\]'

[nim]
format = '\[[$symbol($version)]($style)\]'

[nix_shell]
format = '\[[$symbol$state( \($name\))]($style)\]'

[nodejs]
format = '\[[$symbol($version)]($style)\]'

[ocaml]
format = '\[[$symbol($version)(\($switch_indicator$switch_name\))]($style)\]'

[odin]
format = '\[[$symbol($version )]($style)\]'

[opa]
format = '\[[$symbol($version)]($style)\]'

[openstack]
format = '\[[$symbol$cloud(\($project\))]($style)\]'

[os]
format = '\[[$symbol]($style)\]'

[package]
format = '\[[$symbol$version]($style)\]'

[perl]
format = '\[[$symbol($version)]($style)\]'

[php]
format = '\[[$symbol($version)]($style)\]'

[pijul_channel]
format = '\[[$symbol$channel]($style)\]'

[pixi]
format = '\[[$symbol$version( $environment)]($style)\]'

[pulumi]
format = '\[[$symbol$stack]($style)\]'

[purescript]
format = '\[[$symbol($version)]($style)\]'

[python]
format = '\[[${symbol}${pyenv_prefix}(${version})(\($virtualenv\))]($style)\]'

[quarto]
format = '\[[$symbol($version)]($style)\]'

[raku]
format = '\[[$symbol($version-$vm_version)]($style)\]'

[red]
format = '\[[$symbol($version)]($style)\]'

[rlang]
format = '\[[$symbol($version)]($style)\]'

[ruby]
format = '\[[$symbol($version)]($style)\]'

[rust]
format = '\[[$symbol($version)]($style)\]'

[scala]
format = '\[[$symbol($version)]($style)\]'

[shell]
format = '\[[$indicator]($style)\]'

[singularity]
format = '\[[$symbol\[$env\]]($style)\]'

[solidity]
format = '\[[$symbol($version)]($style)\]'

[spack]
format = '\[[$symbol$environment]($style)\]'

[status]
format = '\[[$symbol$status]($style)\]'

[sudo]
format = '\[[as $symbol]($style)\]'

[swift]
format = '\[[$symbol($version)]($style)\]'

[terraform]
format = '\[[$symbol$workspace]($style)\]'

[time]
format = '\[[$time]($style)\]'

[typst]
format = '\[[$symbol($version)]($style)\]'

[username]
format = '\[[$user]($style)\]'

[vagrant]
format = '\[[$symbol($version)]($style)\]'

[vcsh]
format = '\[vcsh [$symbol$repo]($style)\]'

[vlang]
format = '\[[$symbol($version)]($style)\]'

[xmake]
format = '\[[$symbol($version)]($style)\]'

[zig]
format = '\[[$symbol($version)]($style)\]'
EOF
history -c && >~/.bash_history && history -w
exit
