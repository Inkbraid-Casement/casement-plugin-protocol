# Casement plugin protocol

Casement is a remote desktop client for Windows by Inkbraid. It supports
SPICE, VNC, Remote Desktop, SSH and KVM-over-IP devices.

Protocol plugins add connection types that Casement doesn't support itself.
A plugin is a separate program that Casement starts for each connection. The
two communicate only through the protocol described here:

- Length-prefixed JSON messages over the plugin's standard input and output.
- Screen contents through shared memory provided by Casement.
- Keyboard, mouse and clipboard events in the other direction.

Connection list, saved passwords, tabs, full screen, screenshots, recording
and pop-out windows are implemented in Casement.

Plugins and Casement are separate programs. A plugin can use any licence,
open or closed, and Casement works the same without any plugins installed.

## Contents

| Path | Description |
|---|---|
| [`docs/plugin-protocol.md`](docs/plugin-protocol.md) | Protocol version 1: plugin manifest, connection fields, framing and messages |
| [`examples/mock-plugin/`](examples/mock-plugin/) | A complete plugin in Python (Windows). It draws a test pattern and handles input, cursor and clipboard text. It's used by Casement's tests and is the quickest way to see the protocol work end-to-end. |

## Plugins

| Plugin | Connects to | Address | Protocol | Licence | Download |
|---|---|---|---|---|---|
| [RustDesk](https://github.com/Inkbraid-Casement/casement-plugin-rustdesk) | RustDesk peers, through a self-hosted ID and relay server | `rustdesk://` | 1 | AGPL-3.0 | [Latest release](https://github.com/Inkbraid-Casement/casement-plugin-rustdesk/releases/latest) |
| [JetKVM](https://github.com/Inkbraid-Casement/casement-plugin-jetkvm) | JetKVM devices on the local network | `jetkvm://` | 1 | GPL-2.0-only | [Latest release](https://github.com/Inkbraid-Casement/casement-plugin-jetkvm/releases/latest) |
| [MeshCentral](https://github.com/Inkbraid-Casement/casement-plugin-meshcentral) | Devices managed by a MeshCentral server, through their agents | `meshcentral://` | 1 | Apache-2.0 | [Latest release](https://github.com/Inkbraid-Casement/casement-plugin-meshcentral/releases/latest) |
| [VMware console](https://github.com/Inkbraid-Casement/casement-plugin-webmks) | Virtual machine consoles on ESXi and vCenter Server (WebMKS) | `vmware://` | 1 | GPL-2.0-or-later | [Latest release](https://github.com/Inkbraid-Casement/casement-plugin-webmks/releases/latest) |
| [Moonlight](https://github.com/Inkbraid-Casement/casement-plugin-moonlight) | Desktop and game streaming from Sunshine and GeForce Experience hosts | `moonlight://` | 1 | GPL-3.0-or-later | [Latest release](https://github.com/Inkbraid-Casement/casement-plugin-moonlight/releases/latest) |
| [Mosh](https://github.com/Inkbraid-Casement/casement-plugin-mosh) | Mosh shells, with `mosh-server` started over SSH | `mosh://` | 2 | GPL-3.0-or-later with the OpenSSL exception | [Latest release](https://github.com/Inkbraid-Casement/casement-plugin-mosh/releases/latest) |
| [X2Go](https://github.com/Inkbraid-Casement/casement-plugin-x2go) | X2Go desktop sessions (KDrive) over SSH | `x2go://` | 1 | GPL-3.0-or-later | [Latest release](https://github.com/Inkbraid-Casement/casement-plugin-x2go/releases/latest) |

Each release has a zip with the plugin's folder. To install a plugin, unpack
it into `%LOCALAPPDATA%\Casement\plugins\`, so that
`%LOCALAPPDATA%\Casement\plugins\<plugin>\plugin.json` exists, and restart
Casement. **Plugins…** in Casement's main menu lists the installed plugins.

Mosh shows a terminal rather than a picture, so it needs protocol version 2
with a terminal view, a proposed addition its repository describes in
`docs/terminal-view.md`. The others use version 1.

To write a plugin, start with the mock plugin, then read the spec.

## Versions

The protocol has a version number, which is agreed between plugin and host
in the first message. Unknown message types are ignored, so this should
work even if the host protocol is updated. Breaking changes are listed at
the end of the spec.

## Licence

- The protocol description (`docs/` and this README) is licensed under
  [Creative Commons Attribution 4.0 International](LICENSE-CC-BY-4.0.txt)
  (CC BY 4.0).
- The example code (`examples/`) is licensed under the
  [MIT License](LICENSE-MIT.txt).

Implementing the protocol, in any program under any licence, requires no
permission.
