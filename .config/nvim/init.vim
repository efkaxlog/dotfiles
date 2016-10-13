" set the runtime path to include Vundle and initialize
set rtp+=~/.config/nvim/bundle/Vundle.vim
" call vundle#begin()
" alternatively, pass a path where Vundle should install plugins
call vundle#begin('~/.config/nvim/bundle')

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'
"Plugin 'deoplete.nvim'
Plugin 'vim-airline/vim-airline'
Plugin 'vim-fugitive'
Plugin 'vim-hybrid-material'
" all Vundle plugins must be added before following line
call vundle#end()            " required

set expandtab
set tabstop=4
set shiftwidth=4
inoremap <S-Tab> <C-V><Tab>
filetype indent on
filetype plugin indent on
set number
set pastetoggle=<F2>
set hlsearch
set background=dark
set t_Co=16
colorscheme hybrid_reverse
set nocompatible              " be iMproved, required
filetype off                  " required
