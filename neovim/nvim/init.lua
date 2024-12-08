require("config.lazy")

vim.o.expandtab = true
vim.o.tabstop = 2
vim.o.shiftwidth = 2

vim.api.nvim_set_keymap('i', 'jk', '<ESC>', { noremap = true, silent = true })

