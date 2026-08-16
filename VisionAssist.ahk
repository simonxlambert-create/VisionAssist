; ==============================================================================
; VisionAssist - AutoHotkey Script (RP & Low Vision Accessibility)
; ==============================================================================
#NoEnv
#SingleInstance Force
SetWorkingDir %A_ScriptDir%

global isRed := 0
global cursorSize := 32
global redCursorDir := A_ScriptDir . "\cursors\red"

Menu, Tray, NoStandard
Menu, Tray, Add, VisionAssist (RP Helper), MenuHeader
Menu, Tray, Disable, VisionAssist (RP Helper)
Menu, Tray, Add
Menu, Tray, Add, Toggle Red Cursor (Ctrl + * or F8), ToggleRed
Menu, Tray, Add, Toggle Cursor Size (Ctrl + / or F9), ToggleSize
Menu, Tray, Add
Menu, Tray, Add, Exit, ExitApp
Menu, Tray, Tip, VisionAssist (RP Helper)

; ------------------------------------------------------------------------------
; HOTKEYS:
; 1. Red Cursor: Ctrl+* / F8
; 2. Cursor Size: Ctrl+/ / F9
; ------------------------------------------------------------------------------
^NumpadMult::Gosub, ToggleRed
^+8::Gosub, ToggleRed
F8::Gosub, ToggleRed

^NumpadDiv::Gosub, ToggleSize
^/::Gosub, ToggleSize
F9::Gosub, ToggleSize

; ------------------------------------------------------------------------------
; Subroutines
; ------------------------------------------------------------------------------
ToggleRed:
    isRed := !isRed
    if (isRed)
    {
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, (default), VisionAssist Red
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, Arrow, %redCursorDir%\red_arrow.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, Hand, %redCursorDir%\red_hand.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, IBeam, %redCursorDir%\red_ibeam.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, Crosshair, %redCursorDir%\red_cross.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, No, %redCursorDir%\red_no.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, SizeAll, %redCursorDir%\red_move.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, SizeNS, %redCursorDir%\red_sizens.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, SizeWE, %redCursorDir%\red_sizewe.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, SizeNWSE, %redCursorDir%\red_sizenwse.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, SizeNESW, %redCursorDir%\red_sizenesw.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, UpArrow, %redCursorDir%\red_arrow.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, Help, %redCursorDir%\red_arrow.cur
        SoundBeep, 600, 80
        SoundBeep, 900, 120
    }
    else
    {
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, (default), Windows standaard
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, Arrow, %A_WinDir%\cursors\aero_arrow.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, Hand, %A_WinDir%\cursors\aero_link.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, IBeam, 
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, Crosshair, 
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, No, %A_WinDir%\cursors\aero_unavail.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, SizeAll, %A_WinDir%\cursors\aero_move.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, SizeNS, %A_WinDir%\cursors\aero_ns.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, SizeWE, %A_WinDir%\cursors\aero_ew.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, SizeNWSE, %A_WinDir%\cursors\aero_nwse.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, SizeNESW, %A_WinDir%\cursors\aero_nesw.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, UpArrow, %A_WinDir%\cursors\aero_up.cur
        RegWrite, REG_SZ, HKCU, Control Panel\Cursors, Help, %A_WinDir%\cursors\aero_helpsel.cur
        SoundBeep, 900, 80
        SoundBeep, 600, 120
    }
    DllCall("SystemParametersInfo", "UInt", 0x0057, "UInt", 0, "UInt", 0, "UInt", 0)
return

ToggleSize:
    if (cursorSize = 32)
    {
        cursorSize := 64
        SoundBeep, 900, 120
    }
    else if (cursorSize = 64)
    {
        cursorSize := 96
        SoundBeep, 1200, 120
    }
    else
    {
        cursorSize := 32
        SoundBeep, 500, 120
    }
    RegWrite, REG_DWORD, HKCU, Control Panel\Cursors, CursorBaseSize, %cursorSize%
    DllCall("SystemParametersInfo", "UInt", 0x0057, "UInt", 0, "UInt", 0, "UInt", 0)
return

MenuHeader:
return

ExitApp:
    ExitApp
