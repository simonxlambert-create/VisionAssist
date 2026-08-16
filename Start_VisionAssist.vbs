Set WshShell = CreateObject("WScript.Shell")
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
pythonwPath = "C:\Users\simon\AppData\Local\Programs\Python\Python313\pythonw.exe"
mainScript = scriptDir & "\main.py"

WshShell.CurrentDirectory = scriptDir
WshShell.Run """" & pythonwPath & """ """ & mainScript & """", 0, False
