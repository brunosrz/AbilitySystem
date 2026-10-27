# AGENTS.md - Instruções para Agentes de IA

**Última atualização**: 2026-10-27

---

## ⚠️ REGRAS OBRIGATÓRIAS

### Git Workflow

**ANTES DE QUALQUER `git add` OU `git commit`:**

```bash
python -m pre_commit run --all-files
```

**POR QUÊ:**

- Valida formatação (ruff, prettier, clang-format)
- Verifica copyright headers
- Valida XML/JSON
- Executa linters (mypy, codespell, etc)
- **NUNCA faça commit sem passar em todos os 15 hooks**

### Exemplo Correto de Workflow:

```bash
# 1. Fazer mudanças nos arquivos
# ... edit files ...

# 2. OBRIGATÓRIO: Rodar pre-commit
python -m pre_commit run --all-files

# 3. Se passou ✅: fazer git add
git add file1.gd file2.py ...

# 4. Fazer commit
git commit -m "Mensagem descritiva"

# 5. Push
git push origin dev
```

### Se pre-commit falhar:

```bash
# Alguns hooks auto-corrigem (prettier, ruff-format, etc)
# Re-rodar para validar

python -m pre_commit run --all-files

# Se ainda falhar, debugar:
# - ruff-format: Python formatting issues
# - clang-format: C++ formatting issues
# - codespell: Typos in comments
# - make-rst: Documentation build errors
```

---

## 🎯 DESENVOLVIMENTO MULTIPLAYER

### Status Atual (2026-04-04)

**Infraestrutura Pronta:**

- ✅ GitHub Actions build da demo
- ✅ MultiplayerGameManager (server/client)
- ✅ Dynamic player spawning (1 server + 10 clients)
- ✅ Player AI (GDScript básico)

**Em Desenvolvimento:**

- 🔄 Latência simulada
- 🔄 Chaos engine (kill/restart aleatório)
- 🔄 LimboAI behavior tree completo

### Arquivos Críticos

| Arquivo                                       | Responsabilidade                        |
| --------------------------------------------- | --------------------------------------- |
| `demo/autoload/MultiplayerGameManager.gd`     | Setup ENet, spawn players, snapshots    |
| `demo/player/player_ai.gd`                    | AI behaviors (Walk, Jump, Dash, Attack) |
| `demo/player/player.gd`                       | Player core + multiplayer integration   |
| `utility/multiplayer/runner.py`               | Orchestration + latência + chaos        |
| `.github/workflows/test_multiplayer.yml`      | GHA pipeline (build + test)             |
| `src/tests/bridge/test_as_multiplayer_sync.h` | C++ sync tests                          |
| `src/tests/bridge/test_as_prediction.h`       | C++ prediction tests                    |

### Próximas Tarefas

1. **Latência Simulada** (utility/multiplayer/runner.py)
   - Adicionar `MP_SIMULATED_LATENCY_MS` env var
   - Implementar `time.sleep()` antes de RPC calls
   - Testar com 50-200ms range

2. **Chaos Engine** (utility/multiplayer/runner.py)
   - Thread que mata/reinicia clientes aleatoriamente
   - Stress test network + snapshot recovery
   - Validar state consistency

3. **LimboAI Behavior Tree** (demo/resources/behavior_trees/mp_player_ai.tres)
   - Recriar player_ai.gd como BehaviorTree
   - Tasks: Patrol, Combat, Ability Use
   - Integrar com MultiplayerSynchronizer

---

## 📋 Pre-commit Hooks

Todos os 15 hooks devem passar:

```
✅ validate-xml
✅ doc-source-generator
✅ copyright-headers
✅ file-format
✅ prettier
✅ check-shebangs
✅ check-executables
✅ clang-format
✅ clang-format-glsl
✅ ruff-check
✅ ruff-format
✅ mypy
✅ no-unicode-replacement-chars
✅ codespell
✅ make-rst
```

Se algum falhar, o pre-commit hook output mostrará como corrigir.

---

## 🔗 Referências

- Plano Original: `IMPLEMENTATION_PLAN_MULTIPLAYER_ROBUST_FINAL.md`
- Resumo Implementação: `MULTIPLAYER_IMPLEMENTATION_SUMMARY.md`
- Plano Atual: `.claude/plans/jaunty-enchanting-star.md`

---

## 📦 Publicação na Godot Asset Library

O alvo de compatibilidade desta linha é a versão estável **Godot 4.7.2**. A versão 4.8
é beta e não pode ser usada como evidência de compatibilidade estável.

Antes de criar uma tag ou submeter o asset:

1. Execute `python utility/validate_asset_library.py`.
2. Execute a suíte nativa e o smoke test headless no mesmo commit.
3. Gere o pacote somente com `addons/ability_system`, incluindo `README.md`, `LICENSE`,
   `plugin.cfg`, o `.gdextension`, ícone e as bibliotecas compiladas suportadas.
4. Registre no release quais plataformas foram compiladas e quais ficaram `skipped`.
5. Use a URL pública de navegação do repositório e a URL direta do ícone no formulário da
   Asset Library; não use uma URL de clone `.git`.

Um build verde não substitui a prova de carregamento da GDExtension. Mudanças de runtime
exigem testes de caso feliz, negativos e de regressão. Testes live indisponíveis devem
permanecer explicitamente classificados como `skipped`, nunca como aprovados.
