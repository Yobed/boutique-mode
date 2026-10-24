Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c node services/elsi-whatsapp-bot/server.js", 0, False
