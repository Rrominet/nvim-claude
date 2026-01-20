import pynvim
import subprocess
import json
import sys
import os
import tempfile
import webbrowser
from ml import fileTools as ft

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + os.sep + "anthropic-sdk-python/src")
import anthropic

base_context = """
You respond only Python code that will be directly executed (via python -c "your code").
Do not write anything else than the code.
No intro, no conclusion, just Python code, alone.
Don't rewrite the code as is. Your code should be executable.
Often you will need to write in file. Do not just rewrite the code you need to modify as an anwser.
Actually write the code you should modify or create in the correct file using python.
If you add any text that is not your code, the execution will fail and you ll have completly failed your task.
Add <<<PYTHON_CODE>>> before and after your code.
"""

class AI : 
    @staticmethod
    def execute_python(code, python_exec) : 
        cmd = [python_exec, "-c", code]
        pc = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        res = pc.stdout.decode("utf-8")
        err = pc.stderr.decode("utf-8")
        ret_code = pc.returncode
        return ret_code, res, err

    @staticmethod
    def send_n_execute(client, to_send, model, context, py_exec, max_tokens=8128*2) : 
        messages = [{"role": "user", "content": to_send}]
        try : 
            res = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=context,
                messages = messages
            )
        except Exception as e : 
            return "Error : the Claude API call failed : " + str(e)

        pycode = res.content[0].text
        pycode = pycode.replace ("```python", "")
        pycode = pycode.replace ("```", "")
        try : 
            pycode = pycode.split("<<<PYTHON_CODE>>>")[1]
        except : 
            return "Error : o code found in response."

        ft.write(pycode, tempfile.gettempdir() + os.sep + "pnvim-coder.py")
        pyres = AI.execute_python(pycode, py_exec)

        if (pyres[0] == 0) : 
            return ""
        else : 
            return "Error in Python execution : " + pyres[2]

    @staticmethod
    def send(client, to_send, model, context, py_exec, max_tokens=8128*2) : 
        messages = [{"role": "user", "content": to_send}]
        try : 
            res = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=context,
                messages = messages
            )
        except Exception as e : 
            return "Error : the Claude API call failed : " + str(e)

        return res.content[0].text

@pynvim.plugin
class CoderPlugin:
    def __init__(self, nvim):
        self.nvim = nvim
        self.configpath = os.path.expanduser("~") + "/.config/nvim/coder.json"
        self.docpath = os.path.expanduser("~") + "/.config/nvim/rplugin/python3/coder-data/doc.html"
        self.config = None
        self.active = False
        self.ai = None
        self.py = "/usr/bin/python3"
        self.loadConfig()
        self.load()

    def pwd(self) : 
        return self.nvim.call("getcwd")

    def currentFilepath(self): 
        return os.path.abspath(self.nvim.current.buffer.name)

    def currentLine(self) : 
        return self.nvim.current.line

    def currentLinenumber(self) : 
        return self.nvim.current.window.cursor[0]

    def lineContent(self, lineNumber): 
        return self.nvim.current.buffer[lineNumber - 1]

    def loadConfig(self):
        self.config = None
        if not os.path.exists(self.configpath):
            self.log(f"Config file {self.configpath} not found. Hooks rplugin disabled.")
            return
        try : 
            self.config = json.load(open(self.configpath))
            self.active = True
        except : 
            self.log(f"Config file {self.configpath} founded but not JSON parsable. Hooks rplugin disabled.")
            pass

    def load(self) : 
        if os.path.exists("/usr/bin/python3"): 
            self.py = "/usr/bin/python3"
        elif os.path.exists("/usr/bin/python"): 
            self.py = "/usr/bin/python"
        elif os.path.exists("/usr/local/bin/python3"): 
            self.py = "/usr/local/bin/python3"
        elif os.path.exists("/usr/local/bin/python"): 
            self.py = "/usr/local/bin/python"
        else : 
            self.py = "python3"

        self.ai = anthropic.Anthropic(api_key=self.config["api_key"])

    @pynvim.command('AIImplement', nargs='0', range="")
    def implementCurrentFunc(self, args, range):
        context = base_context
        context += """
Current line :\n""" + self.currentLine() + """\n
Current Working directory : """ + self.pwd() + """
Current Filepath : """ + self.currentFilepath() + """
Current File Content :\n""" + ft.read(self.currentFilepath())

        ask = "Implement the function in the current line. To do this, write me the python code that would modify the current file to add the implementation. (if it's .h file, your code must implement the code in the equivalent .cpp file. If inexistant, create it. - unless it's a template, in that case implement it in the current file.) Respect as much as you can the current file syntax and code logic."

        self.log("Executing in background...")
        error = AI.send_n_execute(self.ai, ask, self.config["model"], context, self.py)
        if error != "" : 
            self.log(error)
            return
        self.nvim.command(":e " + self.currentFilepath()) 
        self.log("Done !")

    @pynvim.command('AIDocument', nargs='0', range="")
    def documentCurrentLine(self, args, range):
        context = base_context
        context += """
Current line :\n""" + self.currentLine() + """\n
Current Filepath : """ + self.currentFilepath() + """
Current File Content :\n""" + ft.read(self.currentFilepath())

        ask = "Don't change the code of the current file, just add the necessary comments above the current line for the function on the current line"

        error = AI.send_n_execute(self.ai, ask, self.config["model"], context, self.py)
        if error != "" : 
            self.log(error)
            return
        self.nvim.command(":e " + self.currentFilepath()) 

    @pynvim.command('AIDocumentFile', nargs='0', range="")
    def documentCurrentFile(self, args, range):
        context = base_context
        context += """
Current Filepath : """ + self.currentFilepath() + """
Current File Content :\n""" + ft.read(self.currentFilepath())

        ask = "Don't change the code of the current file, just add the necessary comments for each function/method/class/variable so someone that does not know the code understand what's going on."

        error = AI.send_n_execute(self.ai, ask, self.config["model"], context, self.py)
        if error != "" : 
            self.log(error)
            return
        self.nvim.command(":e " + self.currentFilepath()) 

    @pynvim.command('AISuggestFromCurrentFile', nargs='*', range='')
    def suggestCurrentFile(self, args, range):
        context = """
Current File Content :\n""" + ft.read(self.currentFilepath())

        ask = "From the code in the current file content, what would you change and make better, more readable, more optimized ?"

        res = AI.send(self.ai, ask, self.config["model"], context, self.py)
        if res[0:5] == "Error" : 
            self.log(error)
            return
        ft.write(res, tempfile.gettempdir() + os.sep + "coder-response")
        self.nvim.command(":vs")
        self.nvim.command(":e " + tempfile.gettempdir() + os.sep + "coder-response") 

    @pynvim.command('AISuggestFromCurrentLine', nargs='*', range='')
    def suggestCurrentLine(self, args, range):
        context = """
Current line :\n""" + self.currentLine() + """\n
Current File Content :\n""" + ft.read(self.currentFilepath())

        ask = "In the function/method on the current line, what would you change to make it better, more readable, more optimized ?"

        res = AI.send(self.ai, ask, self.config["model"], context, self.py)
        if res[0:5] == "Error" : 
            self.log(error)
            return
        ft.write(res, tempfile.gettempdir() + os.sep + "coder-response")
        self.nvim.command(":vs")
        self.nvim.command(":e " + tempfile.gettempdir() + os.sep + "coder-response") 

    def getProjectFiles(self) :
        buffers = self.nvim.buffers
        paths = []
        for buf in buffers:
            # buf.name gives you the full absolute path
            if buf.name:  # Some buffers don't have names (like empty ones)
                paths.append(buf.name)
        return paths

    @pynvim.command('AISuggestFromCurrentProject', nargs='*', range='')
    def suggestCurrentProject(self, args, range):
        context = """
Current File Content :\n""" + ft.read(self.currentFilepath())

        context += "\nAll the files in the current project :\n"
        for path in self.getProjectFiles() :
            context += "\n" + path + ": \n" + ft.read(path) + "\n"

        ask = "From the code in all the files that made this project, what would you change and make better, more readable, more optimized ?"

        res = AI.send(self.ai, ask, self.config["model"], context, self.py)
        if res[0:5] == "Error" : 
            self.log(error)
            return
        ft.write(res, tempfile.gettempdir() + os.sep + "coder-response")
        self.nvim.command(":vs")
        self.nvim.command(":e " + tempfile.gettempdir() + os.sep + "coder-response") 

    @pynvim.command('AIImplementSuggestions', nargs='*', range='')
    def implementSuggest(self, args, range):
        if not os.path.exists(ft.parent(tempfile.gettempdir() + os.sep + "coder-response")) : 
            self.log("No suggestion found.")
            return

        context = base_context
        context += """
Current Filepath : """ + self.currentFilepath() + """
Current File Content :\n""" + ft.read(self.currentFilepath())

        ask = "You gaved me these recommandations : \n" + ft.read(tempfile.gettempdir() + os.sep + "coder-response") + "\n\nImplement them."

        error = AI.send_n_execute(self.ai, ask, self.config["model"], context, self.py)
        if error != "" : 
            self.log(error)
            return
        self.nvim.command(":e " + self.currentFilepath()) 

    @pynvim.command('AIAsk', nargs='*', range='')
    def ask(self, args, range):
        filepath = tempfile.gettempdir() + os.sep + "ask-coder"
        self.nvim.command(":vs")
        try: 
            os.remove(filepath)
        except : pass
        self.nvim.command(":e " + filepath)

    @pynvim.command('AIExec', nargs='0', range="")
    def implementCurrentAsk(self, args, range):
        if not os.path.exists(tempfile.gettempdir() + os.sep + "ask-coder") :
            self.log("No ask found.")
            return
        context = base_context
        context += """
Current line :\n""" + self.currentLine() + """\n
Current Working directory : """ + self.pwd() + """
Current Filepath : """ + self.currentFilepath() + """
Current File Content :\n""" + ft.read(self.currentFilepath())

        ask = ft.read(tempfile.gettempdir() + os.sep + "ask-coder")
        self.log("Executing in background...")
        error = AI.send_n_execute(self.ai, ask, self.config["model"], context, self.py)
        if error != "" : 
            self.log(error)
            return
        self.log("Done !")

    @pynvim.command('AIExecAll', nargs='0', range="")
    def implementCurrentAskAllBuffers(self, args, range):
        if not os.path.exists(tempfile.gettempdir() + os.sep + "ask-coder") :
            self.log("No ask found.")
            return
        context = base_context
        context += """
Current line :\n""" + self.currentLine() + """\n
Current Working directory : """ + self.pwd() + """
Current Filepath : """ + self.currentFilepath() + """
Current File Content :\n""" + ft.read(self.currentFilepath())
        context += "\nAll the files in the current project :\n"
        for path in self.getProjectFiles() :
            context += "\n" + path + ": \n" + ft.read(path) + "\n"

        ask = ft.read(tempfile.gettempdir() + os.sep + "ask-coder")
        self.log("Executing in background...")
        error = AI.send_n_execute(self.ai, ask, self.config["model"], context, self.py)
        if error != "" : 
            self.log(error)
            return
        self.log("Done !")

    @pynvim.command('AIRespond', nargs='0', range="")
    def respondToCurrentAsk(self, args, range):
        if not os.path.exists(tempfile.gettempdir() + os.sep + "ask-coder") :
            self.log("No ask found.")
            return
        context = """
Current line :\n""" + self.currentLine() + """\n
Current Working directory : """ + self.pwd() + """
Current Filepath : """ + self.currentFilepath() + """
Current File Content :\n""" + ft.read(self.currentFilepath())

        ask = ft.read(tempfile.gettempdir() + os.sep + "ask-coder")
        self.log("Executing in background...")
        res = AI.send(self.ai, ask, self.config["model"], context, self.py)
        if res[0:5] == "Error" : 
            self.log(error)
            return
        ft.write(res, tempfile.gettempdir() + os.sep + "coder-response")
        self.nvim.command(":vs")
        self.nvim.command(":e " + tempfile.gettempdir() + os.sep + "coder-response") 

    @pynvim.command('AIRespondAll', nargs='0', range="")
    def respondToCurrentAskAll(self, args, range):
        if not os.path.exists(tempfile.gettempdir() + os.sep + "ask-coder") :
            self.log("No ask found.")
            return
        context = """
Current line :\n""" + self.currentLine() + """\n
Current Working directory : """ + self.pwd() + """
Current Filepath : """ + self.currentFilepath() + """
Current File Content :\n""" + ft.read(self.currentFilepath())
        context += "\nAll the files in the current project :\n"
        for path in self.getProjectFiles() :
            context += "\n" + path + ": \n" + ft.read(path) + "\n"

        ask = ft.read(tempfile.gettempdir() + os.sep + "ask-coder")
        self.log("Executing in background...")
        res = AI.send(self.ai, ask, self.config["model"], context, self.py)
        if res[0:5] == "Error" : 
            self.log(error)
            return
        ft.write(res, tempfile.gettempdir() + os.sep + "coder-response")
        self.nvim.command(":vs")
        self.nvim.command(":e " + tempfile.gettempdir() + os.sep + "coder-response") 

    def log(self, msg):
        self.nvim.out_write(str(msg) + "\n")

    @pynvim.command('AIConfig', nargs='*', range='')
    def openConfig(self, args, range): 
        if not os.path.isdir(ft.parent(self.configpath)) : 
            os.makedirs(ft.parent(self.configpath))
        self.nvim.command(":e " + self.configpath)

    @pynvim.command('AIDebug', nargs='*', range='')
    def openLastPyScript(self, args, range): 
        self.nvim.command(":e " + tempfile.gettempdir() + os.sep + "pnvim-coder.py")
    
    @pynvim.command('AIReload', nargs='*', range='')
    def reloadConfig(self, args, range):
        self.loadConfig()

    @pynvim.command('AIDoc', nargs='*', range='')
    def openDoc(self, args, range):
        webbrowser.open("file:///" + self.docpath)
