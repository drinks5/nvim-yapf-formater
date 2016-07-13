# nvim-yapf-formater
yapf formatter in nvim, it's use the async feature of neovim!


##Feathers
* async, when excute the format command, you can move the cursor free!
* auto find the current tag, and then format it, it was so quickly!
* it use the python client with neovim.


##Normal mode
In normal mode, it will find the range of current tag(function or class) in current line, if fail, if will format the whole buffer

##Visual mode
In visual mode, it will formater the whole buffer
