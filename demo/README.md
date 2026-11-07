# Demo - Ability System v0.1 + Multiplayer RBAC

A complete **Ability System** demo with **Multiplayer, RBAC (Role-Based Access Control), and Admin Tools** support for Godot 4.7.2+.

## 🚀 Quick Start

### Play (New!)

- Open the project
- Press **F5** to run
- Enter your player name
- Choose **Singleplayer** or **Multiplayer**
- Play!

### Test Specific Systems

- **`demo.tscn`** - Original demo's main scene
- **`player/player.tscn`** - Standalone player scene
- **`ui/hud.tscn`** - User interface
- **`tests/test_rbac_scene.tscn`** - RBAC tests

Press **Play (F5)** to run.

### Controls

| Key | Action |
|-------|------|
| **WASD** | Movement (Idle/Walk/Run) |
| **Space** | Jump (Jump/Fall) |
| **Mouse Click** | Attack/Combo |
| **Shift + Click** | Dash Attack |
| **T** | Chat (Multiplayer) |
| **ESC** | Pause Menu (Stop game) |

## 📚 Documentation

### New! Multiplayer & RBAC System

- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - Quick start guide for playing
- **[RBAC_SYSTEM_GUIDE.md](RBAC_SYSTEM_GUIDE.md)** - Complete technical documentation for the RBAC system
- **[IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)** - Implementation status and test checklist
- **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** - Final implementation summary

### Original Ability System

- **[ABILITY_SYSTEM_DEMO.md](ABILITY_SYSTEM_DEMO.md)** - Complete architecture and implementation guide
- **[Framework Documentation](../src/doc_classes/)** - Technical API documentation
- **[Business Rules (Portuguese)](../BUSINESS_RULES.pt.md)** - Framework design rules
- **[Implementation Plan](../IMPLEMENTATION_PLAN.md)** - Implementation plan and roadmap

## ✨ New Features - Multiplayer & RBAC

### Multiplayer

- ✅ Singleplayer mode (local)
- ✅ Multiplayer Server mode (host)
- ✅ Multiplayer Client mode (join)
- ✅ Open world to LAN (Open to LAN)
- ✅ Player management
- ✅ Multiplayer chat system

### Admin & Access Control

- ✅ RBAC system (Admin, Moderator, User)
- ✅ 8 Admin Commands (kick, ban, mute, broadcast, etc.)
- ✅ In-game Admin Panel
- ✅ Ban system with automatic expiration
- ✅ CLI terminal for dedicated servers
- ✅ Centralized logging system

## 📂 Structure

```
demo/
├── ui/                          ← Interface (NEW & EXISTING)
│   ├── user_registration.tscn/.gd    ← NEW: Name registration
│   ├── main_menu.tscn/.gd            ← NEW: Main menu
│   ├── admin_panel.tscn/.gd          ← NEW: Admin panel
│   ├── pause_menu.gd                 ← NEW: Pause menu
│   ├── chat_system.tscn/.gd          ← NEW: Chat system
│   ├── hud.tscn/.gd                  ← Existing
│   └── ...
├── autoload/                    ← Global managers
│   ├── RBAC.gd                       ← NEW: Access control
│   ├── AdminCommand.gd               ← NEW: Command processor
│   ├── AdminTerminal.gd              ← NEW: Server CLI
│   ├── ServerLogger.gd               ← NEW: Logging system
│   ├── SystemVerification.gd         ← NEW: System verification
│   ├── MultiplayerGameManager.gd     ← NEW: Multiplayer manager
│   ├── GameData.gd                   ← NEW: Global state
│   └── GameMachine.gd                ← Existing
├── player/                      ← Player logic & assets
│   ├── player.tscn/.gd
│   └── resources/
├── scenes/                      ← Level scenes
│   ├── level.tscn/.gd
│   └── demo.tscn
├── server/                      ← NEW: Dedicated server
│   └── server.tscn/.gd
├── tests/                       ← NEW: Test suite
│   ├── test_rbac_system.gd
│   └── test_rbac_scene.tscn
├── resources/                   ← Ability System data
│   ├── abilities/
│   ├── attributes/
│   ├── effects/
│   ├── cues/
│   └── container/
└── project.godot                ← UPDATED: New autoloads
```

## 🎮 Gameplay

This demo demonstrates:

- ✅ Dynamic movement (Idle → Walk → Run → Jump → Fall)
- ✅ Combo attack system (3x Light → Heavy)
- ✅ Resources (Stamina) with regeneration
- ✅ Dynamic tags for state tracking
- ✅ Reactive UI synchronized with player state
- ✅ Animations synchronized with state

## 🔧 Techniques Used

- **ASComponent**: Central hub for actor logic
- **Abilities**: Abilities activated by input/events
- **Attributes**: Value system (health, stamina, etc.)
- **Tags**: State tracking (NAME, CONDITIONAL, EVENT)
- **Signals**: Reactive UI updates via `tag_changed`
- **Signal Callbacks**: HUD connected to signals, without polling

## 🐛 Debugging

Logs enabled for verification:

```gdscript
# In demo/player/player.gd
[State] Activating motion.idle
[State] Activating motion.walk
[Tag Color] Player color changed to: blue

# In demo/ui/hud.gd
[HUD] tag_changed: ability.combo1 added
[HUD] State updated: idle → walk
[HUD] Weapon updated: unarmed
```

Check Godot's **Output Console** while running.

## ⚡ Performance

- **Zero Polling**: UI updates only when state actually changes
- **Signal-Based**: Uses Godot signals for reactivity
- **Efficient Queries**: O(1) attribute lookup with HashMap

## 🎮 Build Executables

### Automatic (GitHub Actions)

Executables are built automatically when pushing to `master`, `tests`, or `dev`:

```
Windows:    demo_windows_client.exe, demo_windows_server.exe
Linux:      demo_linux_client, demo_linux_server
macOS:      demo_macos_client, demo_macos_server
Android:    demo_android_client.apk, demo_android_server.apk
```

See `.github/workflows/build_demo_executables.yml`.

### Manual (Godot 4.7.2+)

```bash
# Download Godot 4.7.2 and export templates
godot --path . --export-release "Windows Desktop" ../demo_windows_client.exe
godot --path . --export-release "Linux/X11" ../demo_linux_client
```

## 🧪 Test the RBAC System

Open the test scene:

```
demo/tests/test_rbac_scene.tscn
```

Press F5 to run automated tests. Check Godot's output console.

## 📖 Next Steps

To expand the demo:

### Multiplayer System

1. **Add Whitelist**: Allow only specific players
2. **Ban Persistence**: Save the ban list
3. **Audit Log**: Record all admin actions
4. **Rate Limiting**: Prevent command spam

### Original Ability System

1. **Add Abilities**: Create `.tres` files in `resources/abilities/`
2. **Add Effects**: Create `.tres` files in `resources/effects/`
3. **Add Enemies**: Use ASComponent for AI
4. **Improve UI**: Expand `hud.gd` with new panels
5. **Add Persistence**: Use ASStateSnapshot for save/load

## 📞 Support

### Multiplayer & RBAC

See the new documentation:

- [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) - How to play
- [RBAC_SYSTEM_GUIDE.md](RBAC_SYSTEM_GUIDE.md) - Technical documentation
- [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) - Feature checklist

### Original Ability System

See:

- [ABILITY_SYSTEM_DEMO.md](ABILITY_SYSTEM_DEMO.md) - Complete architecture
- [../IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) - Project roadmap
- [../BUSINESS_RULES.pt.md](../BUSINESS_RULES.pt.md) - Design rules

---

**Version**: 0.1 with Multiplayer RBAC | **Godot**: 4.7.2+ | **Language**: GDScript
