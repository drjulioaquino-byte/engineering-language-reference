# Referências de linguagem para engenharia de software

Biblioteca pública para pessoas, equipes, professores e ferramentas.
[English documentation](README.md).

O material combina três necessidades:

- **Significado:** definições selecionadas do SEVOCAB, com fonte e atribuição.
- **Clareza:** um guia de inglês técnico baseado em ASD-STE100.
- **Obrigação:** RFCs 2119 e 8174, com seus textos originais preservados.

## Por onde começar

Leia o [guia de uso](docs/USAGE.md) e o [glossário de trabalho](docs/GLOSSARY.md).
As definições e explicações em português são conteúdo editorial, não traduções
oficiais das normas. Para ferramentas, há [glossary.json](glossary.json) e o
[manifesto de origem](SOURCE.json).

As fontes estão na pasta [references/](references/). A seleção inicial do SEVOCAB
inclui oito termos; não é uma cópia integral do catálogo ou da norma ISO. O guia
STE é uma ajuda não oficial, com licença MIT; o dicionário oficial ASD não foi copiado.

Adote uma definição explícita por contexto. Quando um termo muda uma ação,
acrescente exemplos e testes. Um vocabulário compartilhado ajuda a comunicação,
mas não comprova entendimento idêntico entre pessoas ou inteligências artificiais.

## Atualização e participação

Um GitHub Actions verifica as fontes semanalmente, às segundas-feiras, às
06:00 de Brasília. Também permite execução manual. Quando encontra uma mudança,
publica uma branch separada e informa o link de comparação para revisão ou abertura
manual de PR. A rotina não cria nem aprova PRs, não faz merge e não muda sozinha
as definições de uso. A permissão de criação/aprovação de PRs por workflows fica
desativada. A rotina passa a operar após a integração do workflow
na branch padrão; consulte a aba Actions para conferir as execuções reais.

Todos podem acessar o repositório público e propor melhorias por issues ou PRs.
As licenças originais acompanham as fontes; a nossa licença MIT não substitui
as condições de reprodução das RFCs ou as atribuições do SEVOCAB.

Para conferir localmente, com Python 3.11 ou superior:

```sh
python tools/references.py verify
python -m unittest discover -s tests -v
```
