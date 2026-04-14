#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Flick menu bar app - focus windows with global keyboard shortcuts.'''

import base64
import json
import re
import threading
import time as _time
from pathlib import Path

import rumps
from pynput import keyboard
from AppKit import (
    NSApp, NSWindow, NSView, NSTextField, NSButton, NSScrollView, NSBox,
    NSBackingStoreBuffered, NSWindowStyleMaskTitled, NSWindowStyleMaskClosable,
    NSWindowStyleMaskResizable,
    NSViewWidthSizable, NSViewHeightSizable, NSViewMinYMargin,
    NSOnState, NSOffState,
    NSAppearance, NSFont, NSCursor, NSTrackingArea,
    NSTrackingMouseEnteredAndExited, NSTrackingActiveAlways,
    NSEvent,
    NSColor, NSAttributedString,
    NSForegroundColorAttributeName, NSFontAttributeName,
    NSMutableParagraphStyle, NSParagraphStyleAttributeName,
    NSImage, NSBitmapImageRep, NSPNGFileType,
)
import objc

from AppKit import NSWorkspace
from ApplicationServices import (
    AXIsProcessTrusted,
    AXUIElementCreateApplication, AXUIElementCopyAttributeValue,
    AXUIElementPerformAction, AXUIElementSetAttributeValue,
    kAXErrorSuccess,
)


def isAccessibilityEnabled():
    return AXIsProcessTrusted()
from Foundation import NSNumber
from Quartz import (
    CGWindowListCopyWindowInfo, CGWarpMouseCursorPosition,
    kCGWindowListOptionOnScreenOnly, kCGWindowListExcludeDesktopElements,
    kCGNullWindowID,
    CGEventTapCreate, CGEventTapEnable, CGEventMaskBit,
    CFMachPortCreateRunLoopSource,
    kCGSessionEventTap, kCGHeadInsertEventTap,
    kCGEventTapOptionDefault, kCGEventKeyDown,
)
from Foundation import (
    NSRunLoop, CFRunLoopAddSource, CFRunLoopRemoveSource,
    kCFRunLoopCommonModes, NSOperationQueue,
)

CONFIG_PATH = Path.home() / '.config' / 'flick' / 'shortcuts.json'

_ICON_B64 = (
    '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'
    'NyvHDyieKQb3AAAAAElFTkSuQmCC'
)

def _iconPath():
    path = CONFIG_PATH.parent / 'icon.png'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(_ICON_B64))
    return str(path)

_kCFBooleanTrue = NSNumber.numberWithBool_(True)
_workspace = NSWorkspace.sharedWorkspace()


def _cgNumForAxWin(win):
    from ctypes import CDLL, POINTER, byref, c_void_p, c_uint32
    _hi = CDLL(
        '/System/Library/Frameworks/ApplicationServices.framework'
        '/Frameworks/HIServices.framework/HIServices')
    _hi._AXUIElementGetWindow.argtypes = [c_void_p, POINTER(c_uint32)]
    _hi._AXUIElementGetWindow.restype = c_uint32
    ptr = objc.pyobjc_id(win)
    if not ptr:
        return None
    winID = c_uint32()
    if _hi._AXUIElementGetWindow(ptr, byref(winID)) != 0:
        return None
    return int(winID.value)

_CTRL_KEYS  = {keyboard.Key.ctrl,  keyboard.Key.ctrl_l,  keyboard.Key.ctrl_r}
_ALT_KEYS   = {keyboard.Key.alt,   keyboard.Key.alt_l,   keyboard.Key.alt_r}
_SHIFT_KEYS = {keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r}
_CMD_KEYS   = {keyboard.Key.cmd,   keyboard.Key.cmd_l,   keyboard.Key.cmd_r}
MODIFIER_KEYS = _CTRL_KEYS | _ALT_KEYS | _SHIFT_KEYS | _CMD_KEYS


def loadConfig():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except Exception:
            pass
    return []


def saveConfig(shortcuts):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(shortcuts, indent=2))


def hotkeyToStr(hotkey):
    '''Convert hotkey dict to display string like "⌃⌘E".'''
    if not hotkey:
        return 'Click to record'
    parts = []
    for mod in ['ctrl', 'alt', 'shift', 'cmd']:
        if hotkey.get(mod):
            parts.append({'ctrl': '⌃', 'alt': '⌥', 'shift': '⇧', 'cmd': '⌘'}[mod])
    parts.append(hotkey.get('key', '').upper())
    return ''.join(parts)



class HotkeyRecorder:
    '''Records a keyboard shortcut when activated.'''

    def __init__(self, callback):
        self.callback = callback
        self.recording = False
        self.modifiers = set()
        self.listener = None

    def start(self):
        self.recording = True
        self.modifiers = set()
        self.listener = keyboard.Listener(
            on_press=self.onPress,
            on_release=self.onRelease)
        self.listener.start()

    def stop(self):
        self.recording = False
        if self.listener:
            self.listener.stop()
            self.listener = None

    def onPress(self, key):
        if not self.recording:
            return
        if key in MODIFIER_KEYS:
            self.modifiers.add(key)
        else:
            hasModifiers = len(self.modifiers) > 0
            if key == keyboard.Key.esc and not hasModifiers:
                self.stop()
                self.callback(None)
                return
            hotkey = {
                'ctrl': any(k in self.modifiers for k in
                    [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]),
                'alt': any(k in self.modifiers for k in
                    [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r]),
                'shift': any(k in self.modifiers for k in
                    [keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r]),
                'cmd': any(k in self.modifiers for k in
                    [keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r]),
                'key': key.char if hasattr(key, 'char') and key.char else str(key).replace('Key.', ''),
            }
            self.stop()
            self.callback(hotkey)

    def onRelease(self, key):
        if key in MODIFIER_KEYS:
            self.modifiers.discard(key)


class ButtonTarget(objc.lookUpClass('NSObject')):
    '''Helper class to receive button actions.'''

    @objc.python_method
    def initWithCallback_(self, callback):
        self = objc.super(ButtonTarget, self).init()
        if self is None:
            return None
        self.callback = callback
        return self

    @objc.typedSelector(b'v@:@')
    def action_(self, sender):
        self.callback()



class ClickableButton(NSButton):
    '''Button that shows pointer cursor on hover.'''

    def acceptsFirstResponder(self):
        return True

    def resetCursorRects(self):
        self.addCursorRect_cursor_(self.bounds(), NSCursor.pointingHandCursor())

    def keyDown_(self, event):
        if event.keyCode() in (36, 76):
            self.performClick_(self)
        elif self.nextResponder():
            self.nextResponder().keyDown_(event)


class HoverButton(ClickableButton):
    '''ClickableButton that brightens its layer background on hover.'''

    def mouseEntered_(self, event):
        if self.layer() and hasattr(self, '_hoverColor'):
            self.layer().setBackgroundColor_(self._hoverColor)

    def mouseExited_(self, event):
        if self.layer() and hasattr(self, '_normalColor'):
            self.layer().setBackgroundColor_(self._normalColor)

    def updateTrackingAreas(self):
        objc.super(HoverButton, self).updateTrackingAreas()
        if hasattr(self, '_hoverArea') and self._hoverArea:
            self.removeTrackingArea_(self._hoverArea)
        opts = NSTrackingMouseEnteredAndExited | NSTrackingActiveAlways
        self._hoverArea = (
            NSTrackingArea.alloc().initWithRect_options_owner_userInfo_(
                self.bounds(), opts, self, None))
        self.addTrackingArea_(self._hoverArea)


class FlippedView(NSView):
    '''NSView with y=0 at the top so content flows top-to-bottom.'''

    def isFlipped(self):
        return True


class ShortcutRow(NSView):
    '''A single row in the shortcuts list with app name, hotkey, center checkbox.'''

    @objc.python_method
    def initWithFrame_index_shortcut_delegate_(self, frame, index, shortcut, delegate):
        self = objc.super(ShortcutRow, self).initWithFrame_(frame)
        if self is None:
            return None

        self.index = index
        self.delegate = delegate
        self.shortcut = shortcut
        self.recorder = HotkeyRecorder(self.onHotkeyRecorded)
        self.targets = []

        y = 0

        self.enabledCheck = ClickableButton.alloc().initWithFrame_(
            ((32, y + 3), (28, 28)))
        self.enabledCheck.setButtonType_(3)
        self.enabledCheck.setFont_(NSFont.systemFontOfSize_(17))
        self.enabledCheck.setTitle_('')
        self.enabledCheck.setState_(
            NSOnState if shortcut.get('enabled', True) else NSOffState)
        self.enabledCheck.setToolTip_('Enable or disable this shortcut')
        enabledTarget = ButtonTarget.alloc().initWithCallback_(self.enabledChanged)
        self.targets.append(enabledTarget)
        self.enabledCheck.setTarget_(enabledTarget)
        self.enabledCheck.setAction_('action:')
        self.addSubview_(self.enabledCheck)

        self.appField = NSTextField.alloc().initWithFrame_(((90, y), (155, 34)))
        self.appField.setEditable_(True)
        self.appField.setSelectable_(True)
        self.appField.setBezeled_(True)
        self.appField.setDrawsBackground_(True)
        self.appField.setBezelStyle_(1)
        self.appField.setFont_(NSFont.systemFontOfSize_(14))
        self.appField.setStringValue_(shortcut.get('app', ''))
        self.appField.setPlaceholderString_("Ex 'Slack'")
        appTarget = ButtonTarget.alloc().initWithCallback_(self.appChanged)
        self.targets.append(appTarget)
        self.appField.setTarget_(appTarget)
        self.appField.setAction_('action:')
        self.addSubview_(self.appField)

        self.hotkeyBtn = ClickableButton.alloc().initWithFrame_(((255, y), (155, 34)))
        self.hotkeyBtn.setTitle_(hotkeyToStr(shortcut.get('hotkey')))
        self.hotkeyBtn.setFont_(NSFont.systemFontOfSize_(14))
        self.hotkeyBtn.setBordered_(False)
        self.hotkeyBtn.setWantsLayer_(True)
        hkLayer = self.hotkeyBtn.layer()
        hkLayer.setBackgroundColor_(
            NSColor.colorWithWhite_alpha_(0.12, 1.0).CGColor())
        hkLayer.setCornerRadius_(4.0)
        hkLayer.setBorderWidth_(1.0)
        hkLayer.setBorderColor_(
            NSColor.colorWithWhite_alpha_(0.3, 1.0).CGColor())
        hotkeyTarget = ButtonTarget.alloc().initWithCallback_(self.recordHotkey)
        self.targets.append(hotkeyTarget)
        self.hotkeyBtn.setTarget_(hotkeyTarget)
        self.hotkeyBtn.setAction_('action:')
        self.addSubview_(self.hotkeyBtn)

        clearBtnH = 18
        clearBtnY = y + (34 - clearBtnH) // 2 + 1
        self.clearBtn = ClickableButton.alloc().initWithFrame_(
            ((386, clearBtnY), (20, clearBtnH)))
        self.clearBtn.setTitle_('×')
        self.clearBtn.setFont_(NSFont.systemFontOfSize_(17))
        self.clearBtn.setBordered_(False)
        clearTarget = ButtonTarget.alloc().initWithCallback_(self.clearHotkey)
        self.targets.append(clearTarget)
        self.clearBtn.setTarget_(clearTarget)
        self.clearBtn.setAction_('action:')
        self.addSubview_(self.clearBtn)

        self.centerCheck = ClickableButton.alloc().initWithFrame_(
            ((461, y + 3), (28, 28)))
        self.centerCheck.setButtonType_(3)
        self.centerCheck.setFont_(NSFont.systemFontOfSize_(17))
        self.centerCheck.setTitle_('')
        self.centerCheck.setState_(
            NSOnState if shortcut.get('centerMouse', True) else NSOffState)
        self.centerCheck.setToolTip_('Center mouse in window after focus')
        centerTarget = ButtonTarget.alloc().initWithCallback_(self.centerChanged)
        self.targets.append(centerTarget)
        self.centerCheck.setTarget_(centerTarget)
        self.centerCheck.setAction_('action:')
        self.addSubview_(self.centerCheck)

        self.deleteBtn = ClickableButton.alloc().initWithFrame_(((549, y + 1), (32, 32)))
        self.deleteBtn.setTitle_('❌')
        self.deleteBtn.setFont_(NSFont.systemFontOfSize_(18))
        self.deleteBtn.setBordered_(False)
        self.deleteBtn.setToolTip_('Delete this keyboard shortcut')
        deleteTarget = ButtonTarget.alloc().initWithCallback_(self.deleteRow)
        self.targets.append(deleteTarget)
        self.deleteBtn.setTarget_(deleteTarget)
        self.deleteBtn.setAction_('action:')
        self.addSubview_(self.deleteBtn)

        return self

    @objc.python_method
    def onHotkeyRecorded(self, hotkey):
        self.delegate._syncRowValues()
        if hotkey is None:
            self.hotkeyBtn.setTitle_(hotkeyToStr(self.shortcut.get('hotkey')))
            return
        self.shortcut['hotkey'] = hotkey
        self.hotkeyBtn.setTitle_(hotkeyToStr(hotkey))
        self.delegate.shortcutChanged()

    @objc.python_method
    def enabledChanged(self):
        self.delegate._syncRowValues()
        self.shortcut['enabled'] = self.enabledCheck.state() == NSOnState
        self.delegate.shortcutChanged()

    @objc.python_method
    def appChanged(self):
        self.shortcut['app'] = self.appField.stringValue()
        self.delegate.shortcutChanged()

    @objc.python_method
    def recordHotkey(self):
        self.hotkeyBtn.setTitle_('Recording...')
        self.window().makeFirstResponder_(None)
        self.recorder.start()

    @objc.python_method
    def clearHotkey(self):
        self.delegate._syncRowValues()
        self.shortcut['hotkey'] = None
        self.hotkeyBtn.setTitle_(hotkeyToStr(None))
        self.delegate.shortcutChanged()

    @objc.python_method
    def centerChanged(self):
        self.delegate._syncRowValues()
        self.shortcut['centerMouse'] = self.centerCheck.state() == NSOnState
        self.delegate.shortcutChanged()

    @objc.python_method
    def deleteRow(self):
        self.delegate.deleteShortcut(self.index)


class ConfigWindow(NSWindow):
    '''Configuration window with shortcuts list.'''

    def performKeyEquivalent_(self, event):
        resp = self.firstResponder()
        while resp is not None and resp != self:
            if resp.performKeyEquivalent_(event):
                return True
            resp = resp.nextResponder()
        return True

    def keyDown_(self, event):
        if event.keyCode() == 48:
            if event.modifierFlags() & (1 << 17):
                self.selectPreviousKeyView_(self)
            else:
                self.selectNextKeyView_(self)
        else:
            pass

    def becomeKeyWindow(self):
        objc.super(ConfigWindow, self).becomeKeyWindow()
        if not getattr(self, '_hadFocus', False):
            self._hadFocus = True
            self.makeFirstResponder_(self)

    def windowShouldClose_(self, sender):
        self.closeWindow()
        return False

    @objc.python_method
    def initWithDelegate_(self, delegate):
        self = objc.super(ConfigWindow, self).initWithContentRect_styleMask_backing_defer_(
            ((200, 200), (602, 440)),
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable |
            NSWindowStyleMaskResizable,
            NSBackingStoreBuffered,
            False)
        if self is None:
            return None

        self.setTitle_('🎯 Flick')
        self.setDelegate_(self)
        self.appDelegate = delegate
        self.shortcuts = loadConfig()
        self.rows = []
        self.buttonTargets = []

        darkMode = NSAppearance.appearanceNamed_('NSAppearanceNameDarkAqua')
        self.setAppearance_(darkMode)

        self.contentView().setWantsLayer_(True)
        bgColor = NSColor.controlBackgroundColor()
        self.setBackgroundColor_(bgColor)

        subtitle = NSTextField.labelWithString_(
            'Focus apps with global keyboard shortcuts')
        subtitle.setFrame_(((0, 415), (602, 20)))
        subtitle.setFont_(NSFont.boldSystemFontOfSize_(13))
        subtitle.setAlignment_(2)
        subtitle.setTextColor_(NSColor.whiteColor())
        subtitle.setAutoresizingMask_(NSViewMinYMargin)
        self.contentView().addSubview_(subtitle)

        rule = NSBox.alloc().initWithFrame_(((12, 406), (578, 1)))
        rule.setBoxType_(2)
        rule.setBorderColor_(
            NSColor.lightGrayColor().colorWithAlphaComponent_(0.4))
        rule.setAutoresizingMask_(NSViewMinYMargin)
        self.contentView().addSubview_(rule)

        headerY = 378
        headerFont = NSFont.boldSystemFontOfSize_(13)

        header0 = NSTextField.labelWithString_('Enabled')
        header0.setFrame_(((12, headerY), (68, 20)))
        header0.setFont_(headerFont)
        header0.setAlignment_(2)
        header0.setAutoresizingMask_(NSViewMinYMargin)
        self.contentView().addSubview_(header0)

        header1 = NSTextField.labelWithString_('App Name')
        header1.setFrame_(((90, headerY), (155, 20)))
        header1.setFont_(headerFont)
        header1.setAlignment_(2)
        header1.setAutoresizingMask_(NSViewMinYMargin)
        self.contentView().addSubview_(header1)

        header2 = NSTextField.labelWithString_('Keyboard Shortcut')
        header2.setFrame_(((255, headerY), (155, 20)))
        header2.setFont_(headerFont)
        header2.setAlignment_(2)
        header2.setAutoresizingMask_(NSViewMinYMargin)
        self.contentView().addSubview_(header2)

        header3 = NSTextField.labelWithString_('Center Mouse')
        header3.setFrame_(((420, headerY), (110, 20)))
        header3.setFont_(headerFont)
        header3.setAlignment_(2)
        header3.setAutoresizingMask_(NSViewMinYMargin)
        self.contentView().addSubview_(header3)

        header4 = NSTextField.labelWithString_('Delete')
        header4.setFrame_(((540, headerY), (50, 20)))
        header4.setFont_(headerFont)
        header4.setAlignment_(2)
        header4.setAutoresizingMask_(NSViewMinYMargin)
        self.contentView().addSubview_(header4)

        self.scrollView = NSScrollView.alloc().initWithFrame_(
            ((0, 40), (602, 330)))
        self.scrollView.setBorderType_(0)
        self.scrollView.setBackgroundColor_(bgColor)
        self.scrollView.setHasVerticalScroller_(True)
        self.scrollView.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)

        self.containerView = FlippedView.alloc().initWithFrame_(((0, 0), (602, 0)))
        self.scrollView.setDocumentView_(self.containerView)
        self.contentView().addSubview_(self.scrollView)

        self.autoSaveLabel = NSTextField.alloc().initWithFrame_(
            ((356, 10), (156, 20)))
        self.autoSaveLabel.setStringValue_('Changes are autosaved.')
        self.autoSaveLabel.setEditable_(False)
        self.autoSaveLabel.setSelectable_(False)
        self.autoSaveLabel.setBezeled_(False)
        self.autoSaveLabel.setDrawsBackground_(False)
        self.autoSaveLabel.setAlignment_(1)
        self.autoSaveLabel.setFont_(
            NSFont.systemFontOfSize_(NSFont.smallSystemFontSize()))
        self.autoSaveLabel.setTextColor_(
            NSColor.whiteColor().colorWithAlphaComponent_(0.5))
        self.contentView().addSubview_(self.autoSaveLabel)

        self.closeBtn = ClickableButton.alloc().initWithFrame_(((520, 8), (65, 24)))
        self.closeBtn.setTitle_('Close')
        self.closeBtn.setBezelStyle_(1)
        self.closeBtnTarget = ButtonTarget.alloc().initWithCallback_(
            self.closeWindow)
        self.closeBtn.setTarget_(self.closeBtnTarget)
        self.closeBtn.setAction_('action:')
        self.contentView().addSubview_(self.closeBtn)

        self.rebuildRows()
        return self

    @objc.python_method
    def _syncRowValues(self):
        for row in self.rows:
            if 0 <= row.index < len(self.shortcuts):
                self.shortcuts[row.index]['app'] = row.appField.stringValue()
                self.shortcuts[row.index]['enabled'] = (
                    row.enabledCheck.state() == NSOnState)

    @objc.python_method
    def closeWindow(self):
        self._syncRowValues()
        saveConfig(self.shortcuts)
        self.appDelegate.reloadHotkeys()
        self.orderOut_(None)

    @objc.python_method
    def rebuildRows(self):
        for row in self.rows:
            row.removeFromSuperview()
        self.rows = []

        if hasattr(self, 'addBtn') and self.addBtn.superview():
            self.addBtn.removeFromSuperview()

        rowHeight = 34
        rowGap = 8
        addBtnHeight = 34
        n = len(self.shortcuts)
        contentHeight = (
            2 * rowGap + addBtnHeight + n * (rowHeight + rowGap)
        )
        totalHeight = max(contentHeight, 349)
        w = int(self.scrollView.contentSize().width)
        self.containerView.setFrameSize_((w, totalHeight))

        addBtnY = rowGap
        self.addBtn = HoverButton.alloc().initWithFrame_(((90, addBtnY), (155, addBtnHeight)))
        self.addBtn.setBordered_(False)
        self.addBtn.setWantsLayer_(True)
        layer = self.addBtn.layer()
        normalColor = NSColor.colorWithWhite_alpha_(0.28, 1.0).CGColor()
        layer.setBackgroundColor_(normalColor)
        layer.setCornerRadius_(5.0)
        layer.setBorderWidth_(1.0)
        layer.setBorderColor_(
            NSColor.colorWithWhite_alpha_(0.55, 1.0).CGColor())
        self.addBtn._normalColor = normalColor
        self.addBtn._hoverColor = NSColor.colorWithWhite_alpha_(0.38, 1.0).CGColor()
        _para = NSMutableParagraphStyle.alloc().init()
        _para.setAlignment_(2)
        self.addBtn.setAttributedTitle_(
            NSAttributedString.alloc().initWithString_attributes_(
                'Add App Shortcut', {
                    NSForegroundColorAttributeName: NSColor.whiteColor(),
                    NSFontAttributeName: NSFont.systemFontOfSize_(14),
                    NSParagraphStyleAttributeName: _para,
                }))
        self.addBtnTarget = ButtonTarget.alloc().initWithCallback_(self.addShortcut)
        self.addBtn.setTarget_(self.addBtnTarget)
        self.addBtn.setAction_('action:')
        self.containerView.addSubview_(self.addBtn)

        for i, shortcut in enumerate(self.shortcuts):
            y = rowGap + addBtnHeight + rowGap + i * (rowHeight + rowGap)
            row = ShortcutRow.alloc().initWithFrame_index_shortcut_delegate_(
                ((0, y), (w, rowHeight)), i, shortcut, self)
            self.containerView.addSubview_(row)
            self.rows.append(row)

    @objc.python_method
    def addShortcut(self):
        self._syncRowValues()
        self.shortcuts.insert(
            0, {'app': '', 'hotkey': None, 'centerMouse': True, 'enabled': True})
        self.rebuildRows()
        self.shortcutChanged()
        newRow = self.rows[0]
        newRow.scrollRectToVisible_(newRow.bounds())
        self.makeFirstResponder_(newRow.appField)

    @objc.python_method
    def deleteShortcut(self, index):
        if 0 <= index < len(self.shortcuts):
            self._syncRowValues()
            del self.shortcuts[index]
            self.rebuildRows()
            self.shortcutChanged()

    @objc.python_method
    def shortcutChanged(self):
        saveConfig(self.shortcuts)
        self.appDelegate.reloadHotkeys()


_MOD_CTRL  = 1 << 18
_MOD_ALT   = 1 << 19
_MOD_SHIFT = 1 << 17
_MOD_CMD   = 1 << 20
_MOD_MASK  = _MOD_CTRL | _MOD_ALT | _MOD_SHIFT | _MOD_CMD

_TAP_DISABLED = (0xFFFFFFFE, 0xFFFFFFFF)  # timeout, user-input disable events


def _makeTapCallback(app):
    def callback(proxy, type_, event, refcon):
        if type_ in _TAP_DISABLED:
            CGEventTapEnable(app._eventTap, True)
            return event
        try:
            nsEv = NSEvent.eventWithCGEvent_(event)
            flags = int(nsEv.modifierFlags()) & _MOD_MASK
            char = (nsEv.charactersIgnoringModifiers() or '').lower()
            if not char:
                return event
            match = app.hotkeyMap.get((
                bool(flags & _MOD_CTRL), bool(flags & _MOD_ALT),
                bool(flags & _MOD_SHIFT), bool(flags & _MOD_CMD),
                char,
            ))
            if match:
                threading.Thread(
                    target=app.doFlick, args=match, daemon=True).start()
                return None
        except Exception:
            pass
        return event
    return callback


class FlickApp(rumps.App):
    '''Menu bar app for Flick.'''

    def __init__(self):
        super().__init__('Flick', icon=_iconPath(), quit_button=None,
                         template=True)

        from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
        NSApplication.sharedApplication().setActivationPolicy_(
            NSApplicationActivationPolicyAccessory)

        self.menu = [
            rumps.MenuItem('Configure shortcuts', callback=self.showConfig),
            None,
            rumps.MenuItem('Quit', callback=rumps.quit_application),
        ]

        self.configWindow = None
        self._eventTap = None
        self._tapSource = None
        self._tapCallback = None
        self.focusHistory = {}  # {(pid, cgNum): (timestamp, axWindowRef)}
        self._focusObserver = None
        self._axObservers = {}  # pid -> (obs, cb, appRef) kept alive
        self.setupHotkeys()
        self._startFocusTracking()

    @objc.python_method
    def setupHotkeys(self):
        if self._eventTap:
            CGEventTapEnable(self._eventTap, False)
            CFRunLoopRemoveSource(
                NSRunLoop.mainRunLoop().getCFRunLoop(),
                self._tapSource, kCFRunLoopCommonModes)
            self._eventTap = None
            self._tapSource = None
            self._tapCallback = None

        self.shortcuts = loadConfig()
        self.appCache = {}
        self.hotkeyMap = {}
        for sc in self.shortcuts:
            if not sc.get('enabled', True):
                continue
            hk = sc.get('hotkey')
            if hk and sc.get('app'):
                mapKey = (
                    hk.get('ctrl', False), hk.get('alt', False),
                    hk.get('shift', False), hk.get('cmd', False),
                    hk.get('key', '').lower(),
                )
                self.hotkeyMap[mapKey] = (
                    sc['app'], sc.get('centerMouse', True))

        self._tapCallback = _makeTapCallback(self)
        tap = CGEventTapCreate(
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            kCGEventTapOptionDefault,
            CGEventMaskBit(kCGEventKeyDown),
            self._tapCallback,
            None,
        )
        if tap:
            src = CFMachPortCreateRunLoopSource(None, tap, 0)
            CFRunLoopAddSource(
                NSRunLoop.mainRunLoop().getCFRunLoop(),
                src, kCFRunLoopCommonModes)
            CGEventTapEnable(tap, True)
            self._eventTap = tap
            self._tapSource = src

    @objc.python_method
    def _startFocusTracking(self):
        from ctypes import (
            CDLL, CFUNCTYPE, POINTER, byref,
            c_void_p, c_int32, c_uint32, c_char_p,
        )
        from ctypes.util import find_library

        _hi = CDLL(
            '/System/Library/Frameworks/ApplicationServices.framework'
            '/Frameworks/HIServices.framework/HIServices')
        _cf = CDLL(find_library('CoreFoundation'))

        AXCB = CFUNCTYPE(None, c_void_p, c_void_p, c_void_p, c_void_p)
        _hi.AXObserverCreate.argtypes = [c_int32, AXCB, POINTER(c_void_p)]
        _hi.AXObserverCreate.restype = c_int32
        _hi.AXObserverAddNotification.argtypes = [
            c_void_p, c_void_p, c_void_p, c_void_p]
        _hi.AXObserverAddNotification.restype = c_int32
        _hi.AXObserverGetRunLoopSource.argtypes = [c_void_p]
        _hi.AXObserverGetRunLoopSource.restype = c_void_p
        _hi.AXUIElementCreateApplication.argtypes = [c_int32]
        _hi.AXUIElementCreateApplication.restype = c_void_p
        _cf.CFStringCreateWithCString.argtypes = [
            c_void_p, c_char_p, c_uint32]
        _cf.CFStringCreateWithCString.restype = c_void_p
        _cf.CFRelease.argtypes = [c_void_p]
        _cf.CFRunLoopGetMain.restype = c_void_p
        _cf.CFRunLoopAddSource.argtypes = [c_void_p, c_void_p, c_void_p]

        UTF8 = 0x08000100
        kCommonModes = c_void_p.in_dll(_cf, 'kCFRunLoopCommonModes')
        mainLoop = _cf.CFRunLoopGetMain()
        kWinChanged = _cf.CFStringCreateWithCString(
            None, b'AXFocusedWindowChanged', UTF8)

        focusHistory = self.focusHistory
        _observers = self._axObservers

        def _recordFocused(pid, appRef_py):
            err, win = AXUIElementCopyAttributeValue(
                appRef_py, 'AXMainWindow', None)
            if err != kAXErrorSuccess or not win:
                return False
            cgNum = _cgNumForAxWin(win)
            if cgNum is None:
                return False
            focusHistory[(pid, cgNum)] = (_time.time(), win)
            return True

        def _registerApp(pid):
            if pid in _observers:
                return
            appRef_ct = _hi.AXUIElementCreateApplication(pid)
            appRef_py = AXUIElementCreateApplication(pid)

            def _cb(observer, element, notification, refcon):
                try:
                    _recordFocused(pid, appRef_py)
                except Exception:
                    pass

            cb = AXCB(_cb)
            obs = c_void_p()
            if _hi.AXObserverCreate(pid, cb, byref(obs)) != 0:
                return
            _hi.AXObserverAddNotification(
                obs.value, appRef_ct, kWinChanged, None)
            src = _hi.AXObserverGetRunLoopSource(obs.value)
            _cf.CFRunLoopAddSource(mainLoop, src, kCommonModes)
            _observers[pid] = (obs, cb, appRef_py)

        def _retryRecord(pid, attempts=5):
            if not attempts:
                return
            if pid not in _observers:
                _registerApp(pid)
            if pid in _observers:
                if _recordFocused(pid, _observers[pid][2]):
                    return
            threading.Timer(0.5, lambda:
                NSOperationQueue.mainQueue()
                .addOperationWithBlock_(
                    lambda: _retryRecord(pid, attempts - 1))
            ).start()

        for app in _workspace.runningApplications():
            if app.activationPolicy() == 0:
                _registerApp(app.processIdentifier())

        active = _workspace.frontmostApplication()
        if active and active.activationPolicy() == 0:
            try:
                _retryRecord(active.processIdentifier())
            except Exception:
                pass

        def _onActivate(notif):
            try:
                nsApp = notif.userInfo().get(
                    'NSWorkspaceApplicationKey')
                if nsApp and nsApp.activationPolicy() == 0:
                    _retryRecord(nsApp.processIdentifier())
            except Exception:
                pass

        self._focusObserver = (
            _workspace.notificationCenter()
            .addObserverForName_object_queue_usingBlock_(
                'NSWorkspaceDidActivateApplicationNotification',
                None, None, _onActivate))

    @objc.python_method
    def doFlick(self, appName, centerMouse):
        try:
            lower = appName.lower()
            app = self.appCache.get(lower)
            if app is None or app.isTerminated():
                matches = [
                    a for a in _workspace.runningApplications()
                    if a.localizedName()
                    and lower in a.localizedName().lower()
                    and a.activationPolicy() == 0
                ]
                app = min(
                    matches,
                    key=lambda a: len(a.localizedName()),
                    default=None,
                )
                if app:
                    self.appCache[lower] = app
            if not app:
                return
            pid = app.processIdentifier()
            appRef = AXUIElementCreateApplication(pid)

            # Pick the most recently focused window from history
            bestTime = -1
            target = None
            targetCgNum = None
            for (p, cgNum), (t, ref) in self.focusHistory.items():
                if p == pid and t > bestTime:
                    bestTime = t
                    target = ref
                    targetCgNum = cgNum

            # No history — fall back to AXMainWindow
            if target is None:
                errM, mainWin = AXUIElementCopyAttributeValue(
                    appRef, 'AXMainWindow', None)
                if errM != kAXErrorSuccess or not mainWin:
                    return
                target = mainWin
                targetCgNum = _cgNumForAxWin(mainWin)

            # Center mouse before activation (position known before
            # Space switch; centering first avoids a race condition)
            if centerMouse:
                ep, posVal = AXUIElementCopyAttributeValue(
                    target, 'AXPosition', None)
                es, sizeVal = AXUIElementCopyAttributeValue(
                    target, 'AXSize', None)
                if ep == kAXErrorSuccess and es == kAXErrorSuccess:
                    pm = re.search(
                        r'x:([\d.-]+) y:([\d.-]+)', repr(posVal))
                    sm = re.search(
                        r'w:([\d.-]+) h:([\d.-]+)', repr(sizeVal))
                    if pm and sm:
                        x, y = float(pm.group(1)), float(pm.group(2))
                        w, h = float(sm.group(1)), float(sm.group(2))
                        CGWarpMouseCursorPosition((x + w / 2, y + h / 2))

            done = threading.Event()
            def _activate(a=app):
                fromApp = _workspace.frontmostApplication()
                if fromApp and hasattr(a, 'activateFromApplication_'):
                    a.activateFromApplication_(fromApp)
                else:
                    a.activateWithOptions_(2)
                done.set()
            NSOperationQueue.mainQueue().addOperationWithBlock_(_activate)
            done.wait(timeout=1.0)

            AXUIElementSetAttributeValue(
                target, 'AXMain', _kCFBooleanTrue)
            AXUIElementPerformAction(target, 'AXRaise')
            AXUIElementSetAttributeValue(
                target, 'AXFocused', _kCFBooleanTrue)
        except Exception as e:
            rumps.notification('Flick', 'Error', str(e))

    @objc.python_method
    def reloadHotkeys(self):
        self.setupHotkeys()

    def showConfig(self, _):
        if self.configWindow is None:
            self.configWindow = ConfigWindow.alloc().initWithDelegate_(self)
        self.configWindow.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)


try:
    try:
        from importlib.metadata import version as _pkgVersion
    except ImportError:
        from importlib_metadata import version as _pkgVersion
    _VERSION = _pkgVersion('flick')
except Exception:
    _toml = Path(__file__).parent / 'pyproject.toml'
    if _toml.exists():
        _VERSION = re.search(
            r'^version\s*=\s*"([^"]+)"',
            _toml.read_text(), re.M).group(1)
    else:
        _VERSION = 'unknown'

_HELP = '''flick - focus apps by name with global keyboard shortcuts

Usage: flick [options]

Options:
  -h, --help     show this message and exit
  --version      show version and exit

Flick runs as a menu bar app. Click the 🎯 icon in the menu bar to
configure global keyboard shortcuts that focus any app and center the
mouse therein.'''


def main():
    import sys
    if '-h' in sys.argv or '--help' in sys.argv:
        print(_HELP)
        return
    if '--version' in sys.argv:
        print(f'flick {_VERSION}')
        return

    print('Starting flick... click 🎯 in the menu bar to configure.')
    if not isAccessibilityEnabled():
        rumps.alert(
            'Accessibility Required',
            'Grant access in System Settings > Privacy & Security > '
            'Accessibility, then restart Flick.')

    FlickApp().run()


if __name__ == '__main__':
    main()
