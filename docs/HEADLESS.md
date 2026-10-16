# Headless sessions

This fork renders the RDP session on a headless output sized to the client
instead of mirroring a physical monitor. A Full HD or ultrawide client gets
its native resolution, not an upscaled copy of the laptop panel.

## What happens

- **Connect:** hypr-rdp sizes its `hypr-rdp` headless output to the client.
  `bin/session-display start` turns the laptop panel off, so Hyprland moves
  every workspace onto the session.
- **Lid:** while a client is connected, closing the lid does not suspend.
  Omarchy still locks the screen; unlock it from the session.
- **Move the client window to another monitor:** the session resizes to that
  monitor (DisplayControl). This needs the patch in
  `backend/reactivation-keeps-displaycontrol-size.patch`, which the installer
  applies.
- **Disconnect, or the backend dies:** the panel comes back, the workspaces
  return to it, and the lid suspends again.

The panel is switched with Omarchy's own `internal-monitor-disable` flag, so
**Super + Ctrl + Delete** (Omarchy's "Toggle laptop display") brings it back
by hand at any time.

The monitor chosen in Settings is no longer used to capture.

## Required Hyprland config

The headless output exists for as long as the service runs, not just during a
session. Add this to `~/.config/hypr/monitors.lua` so it stays out of the
cursor's reach, keeps off the numbered workspaces, and keeps its last session
size across `hyprctl reload` (hypr-rdp skips resizing to the size it believes
it already has):

```lua
local function rdp_headless_mode()
  local ok, mode = pcall(function()
    local file = io.open(os.getenv("HOME") .. "/.local/state/omarchy-remote-desktop/headless-mode")
    if not file then return nil end
    local line = file:read("l")
    file:close()
    return line
  end)
  if ok and type(mode) == "string" and mode:match("^%d+x%d+@60$") then return mode end
  return "1920x1080@60"
end
hl.monitor({ output = "hypr-rdp", mode = rdp_headless_mode(), position = "-9999x0", scale = 1 })
hl.workspace_rule({ workspace = "name:rdp", monitor = "hypr-rdp", default = true, persistent = true })
```

Then run `hyprctl reload` and check `hyprctl configerrors`.

## Limits

- One client monitor at a time; spanning several (`/multimon`) is not
  supported.
- A `hyprctl reload` during a session puts the output back to the last saved
  size; reconnect if the picture looks wrong.
- Tested with Windows `mstsc` over Tailscale on Hyprland 0.56 and Omarchy.
