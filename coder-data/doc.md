# nvim-coder

## List of all commands

- AIDoc
- AIImplement
- AIDocument
- AIDocumentFile
- AISuggestFromCurrentFile
- AISuggestFromCurrentLine
- AISuggestFromCurrentProject
- AIImplementSuggestions
- AIAsk
- AIExec
- AIExecAll
- AIRespond
- AIRespondAll
- AIConfig
- AIDebug
- AIReload


### AIDoc

Open this document.

### AIImplement

Will implement the content of the function that is written on the line under the cursor.

### AIDocument

Will document the function that is written on the line under the cursor.
The documentation will be add as comments above the function definition.

### AIDocumentFile

Exactly like AiDocument but for the entire file, not only the function under the cursor.

### AISuggestFromCurrentFile

Will ask suggestion for current file code.
The suggestions will be written in `/tmp/coder-response`.

### AISuggestFromCurrentLine

Will ask suggestion for the function written under the cursor.
The suggestions will be written in `/tmp/coder-response`.

### AISuggestFromCurrentProject

Will ask suggestion for all opened buffers in nvim.
(careful here, if you have a lot of buffers, the context sended to claude could be quite long - and so quite expensive)
The suggestions will be written in `/tmp/coder-response`.

### AIImplementSuggestions

Will implement the suggestions written in `/tmp/coder-response`

### AIAsk

Open simply the buffer `/tmp/ask-coder` where you can ask anything to claude.

### AIExec

Execute what is written in `/tmp/ask-coder`.
Claude here will have only the current file as context.

(careful to not have the `/tmp/ask-coder` buffer as current file, otherwise the context will make no sense)

### AIExecAll

Execute what is written in `/tmp/ask-coder`.
Claude here will have all the buffers as context.

### AIRespond

Send to Claude what is written in `/tmp/ask-coder`.
Claude will respond in the buffer `/tmp/coder-response`

Claude will have as context the current file.

### AIRespondAll

Same as `AIRespond` but with all the buffers as context

### AIConfig

Open the file to config the plugin (like the api-keys)

### AIDebug

Open the python file that claude has executed last.
Useful if you have an error in the python execution once Claude has been called.

### AIReload

Reload the plugin from the config file.
No need to rebbot `nvim`.
