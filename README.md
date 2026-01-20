# Coder - Neovim AI Assistant Plugin

A powerful Neovim Python plugin that integrates Claude AI (Anthropic) to assist you with code implementation, documentation, and optimization suggestions.

## Overview

Coder is a remote plugin for Neovim that leverages Claude AI to help developers with various coding tasks directly from their editor. It can implement functions, generate documentation, provide optimization suggestions, and execute custom AI-powered tasks.

## Features

- **Function Implementation**: Automatically implement function stubs based on their signatures
- **Code Documentation**: Generate documentation for functions, methods, classes, and entire files
- **Code Suggestions**: Get AI-powered suggestions for code improvements, optimization, and readability
- **Project-Wide Analysis**: Analyze entire projects across multiple open buffers
- **Custom AI Queries**: Ask custom questions and execute AI-generated Python code
- **Interactive Workflow**: Execute AI suggestions with a single command

> [!NOTE]
> For now, it has only be tested on Linux.

## Installation

First of all, you need to install [pynvim](https://github.com/neovim/pynvim) that is a python client for neovim. (and that's what makes this plugin run so good luck without it !)

Follow the instructions [here](https://github.com/neovim/pynvim?tab=readme-ov-file#install) to install `pynvim` on you machine and come back.

> [!IMPORTANT]
> If you don't have installed `pynvim`, the plugin won't work.
> You can check your installation with the command in `nvim` : `:checkhealth provider` and it should return cometing like this :
```
- INFO: Using: /usr/bin/python3
- INFO: pynvim: yes
```

Now just run the `coder-install` file as `sudo`.

Then, you need to reload the rplugins in `nvim`. 
To do that : 

 - open ` nvim`
 - run `:UpdateRemotePlugins`
 - close `nvim`

You should be good to go !

### Configuration

Create a configuration file at `~/.config/nvim/coder.json`:

```json
{
  "api_key": "your-anthropic-api-key-here",
  "model": "claude-3-5-sonnet-20241022"
}
```

To edit the configuration from `nvim` : 
`:AIConfig`

To reload the config, no need to rebbot `nvim`.  
Just run :  
`:AIReload`

>[!warning]
>You obviously need a `config` file with with valid api-keys and a model name.

## Configuration Options

Currently supported configuration options in `coder.json`:

- `api_key`: Your Anthropic API key (required)
- `model`: Claude model to use 


## Commands and How It Works

Just run `AIDoc` to have the list of all the commands and how they work.

### Code Execution Flow

User Command → Build Context → API Call → Extract Python Code → Execute → Reload File

### Code Execution Errors

1. Check the last generated code: `:AIDebug`
2. Review error messages in Neovim command line
3. Ensure file permissions are correct

## Dependencies

- **pynvim**: Neovim Python client
- **anthropic**: Anthropic SDK for Claude API
- **Standard library**: subprocess, json, sys, os, tempfile

