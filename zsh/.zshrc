# Use powerline
USE_POWERLINE="true"
# Has weird character width
# Example:
#    is not a diamond
HAS_WIDECHARS="false"
# Source manjaro-zsh-configuration
if [[ -e /usr/share/zsh/manjaro-zsh-config ]]; then
  source /usr/share/zsh/manjaro-zsh-config
fi
# Use manjaro zsh prompt
if [[ -e /usr/share/zsh/manjaro-zsh-prompt ]]; then
  source /usr/share/zsh/manjaro-zsh-prompt
fi

# rootless docker
export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock

# Sheldon
eval "$(sheldon source)"

# RubyGems
export GEM_HOME="$(gem env user_gemhome)"
export PATH="$PATH:$GEM_HOME/bin"

# alias
alias ls='ls -F --color=auto'

# abbr
abbr -S ll='ls -l' >>/dev/null
abbr -S la='ls -A' >>/dev/null
abbr -S lla='ls -l -A' >>/dev/null
abbr -S digs='dig +short' >>/dev/null
abbr -S sedie='sed -i -e' >> /dev/null
abbr -S ltdiff='latexdiff-vc -e utf8 --git --flatten --force --graphics-markup=none -r' >> /dev/null

