Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd.exe /c """ & "D:\portfolio\startup\f ga\planner\run_bot.bat" & """", 0, False
Set WshShell = Nothing
