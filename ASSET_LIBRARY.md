# Publicação na Godot Asset Library

## Estado

O AbilitySystem está preparado para uma primeira publicação pública como plugin
GDExtension para **Godot 4.7+**. A versão `0.1.0` deve ser apresentada como lançamento
inicial, não como garantia de estabilidade para todos os jogos e plataformas.

## Pacote submetido

O pacote deve conter `addons/ability_system/` e, dentro dele:

- `plugin.cfg` com nome, descrição, autor, versão, compatibilidade e ícone;
- `ability_system.gdextension`;
- `README.md` em inglês e documentação complementar em português;
- `LICENSE` com o texto MIT e o titular do copyright;
- ícones e as bibliotecas nativas disponíveis para a plataforma do release.

O workflow de publicação usa um download customizado de um GitHub Release quando o
pacote precisa carregar bibliotecas pré-compiladas. Isso evita depender de submódulos,
que não são incluídos nos ZIPs automáticos do GitHub.

## Formulário

Ao submeter, usar:

- repositório: `https://github.com/brunosrz/AbilitySystem`;
- issues: `https://github.com/brunosrz/AbilitySystem/issues`;
- licença: `MIT`;
- versão mínima: `4.7`;
- versão do asset: a tag publicada, por exemplo `0.1.0`;
- download: URL direta do ZIP do release correspondente;
- ícone: URL direta `raw.githubusercontent.com` para um PNG/JPG ou outro formato aceito.

Não submeter o asset antes de anexar evidências do build, do smoke test headless e da
validação de metadados no mesmo commit da tag.
