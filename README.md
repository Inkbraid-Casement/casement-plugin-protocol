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

| Plugin | Address scheme | Repository |
|---|---|---|
| RustDesk (self-hosted ID and relay server) | `rustdesk://` | [Inkbraid/casement-plugin-rustdesk](https://github.com/Inkbraid/casement-plugin-rustdesk) |

To write a plugin, start with the mock plugin, then read the spec. To
install a plugin, copy its folder (with its `plugin.json`) to
`%LOCALAPPDATA%\Casement\plugins\` and restart Casement. **Plugins…** in
Casement's main menu lists the installed plugins.

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
