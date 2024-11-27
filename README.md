# dotfiles
## Requirements
- Python 3.10+

## Usage
### Basic Usage
Install dotfiles
```bash
./dotfiles.py
```
This operation will create symbolic links to the dotfiles and copy old dotfiles to `~/.dotbackup`.

### Add dotfiles
1. Add a directory to `dotfiles` directory (e.g. `dotfiles/zsh`).
2. Add dotfiles (both file/directory ok) to the new directory (e.g. `dotfiles/zsh/.zshrc`).
3. Add `path.json` to the new directory (e.g. `dotfiles/zsh/path.json`) and configure correctly.
4. Run `./dotfiles.py` to install the new dotfiles.

`path.json` must represent a JSON object or an array of JSON objects with the following keys:
- `src`: Source path to a dotfile (e.g. `".zshrc"`). 
- `dst`: Destination path to a dotfile (e.g. `"~/.zshrc"`).
- `is_home` (optional `true`): If `true`, the destination is interpreted as a relative path from the home directory (e.g. `".zshrc"` -> `"~/.zshrc"`). Otherwise, the destination is interpreted as an absolute path (e.g. `"~/zshrc"`).

### Others

usage: `dotfiles.py [-h] [--restore] [--dry-run]`

options:  
- `-h`, `--help`  show this help message and exit  
- `--restore`   Restore dotfiles from backup. (Not implemented yet)
- `--dry-run`   Test run without actual file operations.  

