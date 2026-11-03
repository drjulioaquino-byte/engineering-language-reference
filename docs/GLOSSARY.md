# Working glossary / Glossário de trabalho

Original editorial explanations under MIT. These are not official definitions or translations of standards.
Source context is linked where available; entries without it are explicitly editorial.
Read the original quotations in references/sevocab/ and the original RFCs before adopting a meaning.

| Term | Working definition (English) | Explicação editorial (português) | Source context |
| --- | --- | --- | --- |
| `requirement` | A stated condition or capability that a system or process must satisfy. | Uma condição ou capacidade declarada que o sistema ou processo deve satisfazer. | [requirement.json](../references/sevocab/requirement.json) |
| `verification` | Assess, with objective evidence, whether specified requirements are satisfied. | Avaliar, com evidências objetivas, se os requisitos especificados foram atendidos. | [verification.json](../references/sevocab/verification.json) |
| `validation` | Assess whether a system meets its intended use in the stated context. | Avaliar se o sistema atende ao uso pretendido no contexto declarado. | [validation.json](../references/sevocab/validation.json) |
| `failure` | An observed departure of system behavior from its stated requirements. | Um desvio observado do comportamento do sistema em relação aos requisitos declarados. | [failure.json](../references/sevocab/failure.json) |
| `fault` | An inability to perform as required due to an internal state, in the selected assurance context. | Uma incapacidade de cumprir o exigido devido a um estado interno, no contexto de garantia selecionado. | [fault.json](../references/sevocab/fault.json) |
| `error` | A discrepancy between an observed or computed value and its specified or correct reference. | Uma discrepância entre um valor observado ou calculado e sua referência especificada ou correta. | [error.json](../references/sevocab/error.json) |
| `defect` | A flaw in an artifact relative to an applicable requirement. | Uma deficiência em um artefato em relação a um requisito aplicável. | [defect.json](../references/sevocab/defect.json) |
| `test case` | Inputs, conditions and expected results used to evaluate a specific behavior. | Entradas, condições e resultados esperados usados para avaliar um comportamento específico. | [test-case.json](../references/sevocab/test-case.json) |
| `warning` | A notice of a concern with an explicitly defined response; it does not grant authority. | Um aviso sobre uma preocupação com resposta explicitamente definida; ele não concede autorização. | Editorial only |
| `evidence` | A recorded observation or result used to assess a claim, with its origin and limits. | Uma observação ou resultado registrado para avaliar uma afirmação, com sua origem e seus limites. | Editorial only |
| `hypothesis` | A claim with a defined way to seek supporting observations and counterexamples. | Uma afirmação com uma forma definida de buscar observações de apoio e contraexemplos. | Editorial only |
| `prediction` | A claim recorded before the outcome, with admissible inputs and a defined future horizon. | Uma afirmação registrada antes do resultado, com entradas admissíveis e horizonte futuro definido. | Editorial only |
| `implementer` | The agent that plans and changes code in its own branch and opens the pull request; it cannot merge or decide. | O agente que planeja e altera o código em branch próprio e abre o pull request; não faz merge nem decide. | Editorial only |
| `reviewer` | The agent that audits a plan or pull request with evidence and recommends; it cannot order, write the change or decide. | O agente que audita um plano ou pull request com evidências e recomenda; não dá ordens, não escreve a mudança e não decide. | Editorial only |
| `human authority` | The person who decides what to do, what to correct and whether to merge; no agent holds this role. | A pessoa que decide o que fazer, o que corrigir e se faz o merge; nenhum agente ocupa esse papel. | Editorial only |
| `self-review` | A review produced by the implementer or its own tooling; it is never independent review. | Uma revisão feita pelo implementador ou por suas próprias ferramentas; nunca é revisão independente. | Editorial only |
| `independent review` | A review by a party other than the implementer, bound to one exact head SHA. | Uma revisão feita por alguém diferente do implementador, vinculada a um head SHA exato. | Editorial only |
| `finding` | A numbered review result with location, evidence, consequence, recommendation and a resolution criterion. | Um resultado de revisão numerado, com local, evidência, consequência, recomendação e critério de resolução. | Editorial only |
| `resolution criterion` | The observable result that shows a finding was corrected. | O resultado observável que mostra que um achado foi corrigido. | Editorial only |
| `head SHA` | The full commit identifier of the pull request tip that a review or test applies to. | O identificador completo do commit no topo do pull request ao qual uma revisão ou teste se aplica. | Editorial only |
| `checkpoint` | A record, before a merge decision, of head, base, test results, findings and open comments. | Um registro, antes da decisão de merge, de head, base, resultados de teste, achados e comentários em aberto. | Editorial only |
| `preflight` | A written plan before implementation: order, scope, permissions, exclusions, risks and completion condition. | Um plano escrito antes de implementar: ordem, escopo, permissões, exclusões, riscos e condição de conclusão. | Editorial only |
| `postflight` | A written record after implementation of what was executed, its results and its limits. | Um registro escrito depois de implementar, com o que foi executado, os resultados e os limites. | Editorial only |
| `decision record` | A stored human choice with options, the chosen option, time, validity and the change it authorizes. | Uma escolha humana registrada, com opções, opção escolhida, horário, validade e a mudança que ela autoriza. | Editorial only |
| `bounded order` | A human authorization limited to one scope and one validity period that never includes merge. | Uma autorização humana limitada a um escopo e a um prazo de validade, que nunca inclui o merge. | Editorial only |
| `correction cycle` | Rounds of review and correction inside the scope of one decision; a scope change needs a new decision. | Rodadas de revisão e correção dentro do escopo de uma decisão; mudança de escopo exige nova decisão. | Editorial only |
| `MUST` | An absolute requirement when the specification adopts BCP 14. | Uma exigência obrigatória quando a especificação adota o BCP 14. | [rfc2119.txt](../references/rfc/rfc2119.txt), [rfc8174.txt](../references/rfc/rfc8174.txt) |
| `MUST NOT` | An absolute prohibition when the specification adopts BCP 14. | Uma proibição obrigatória quando a especificação adota o BCP 14. | [rfc2119.txt](../references/rfc/rfc2119.txt), [rfc8174.txt](../references/rfc/rfc8174.txt) |
| `SHOULD` | A recommendation; an exception requires understanding and weighing its implications. | Uma recomendação; uma exceção exige compreender e ponderar suas consequências. | [rfc2119.txt](../references/rfc/rfc2119.txt), [rfc8174.txt](../references/rfc/rfc8174.txt) |
| `SHOULD NOT` | A negative recommendation; an exception requires understanding and weighing its implications. | Uma recomendação contrária; uma exceção exige compreender e ponderar suas consequências. | [rfc2119.txt](../references/rfc/rfc2119.txt), [rfc8174.txt](../references/rfc/rfc8174.txt) |
| `MAY` | An optional choice when the specification adopts BCP 14. | Uma escolha opcional quando a especificação adota o BCP 14. | [rfc2119.txt](../references/rfc/rfc2119.txt), [rfc8174.txt](../references/rfc/rfc8174.txt) |
