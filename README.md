# nvim-yapf-formater
yapf formatter in nvim, it's use the async feature of neovim!


##Feathers
* async, when excute the format command, you can move the cursor free!
* auto find the current tag, and then format it, it was so quickly!
* it use the python client with neovim.

##Install 

    with the vim-plug
    Plug 'drinksober/nvim-yapf-formater'
    
##Normal mode
In normal mode, it will find the range of current tag(function or class) in current line, if fail, if will format the whole buffer

##Visual mode
In visual mode, it will formater the whole buffer

##Example config

    noremap <leader>y :YapfFormat<CR>
    vnoremap <leader>y :YapfFormat 'full'<CR>
  
###use the autocmd with format the scope of the tag

    autocmd BufWritePre * YapfFormater
It inspired by the pignacio/vim-yapf-format
