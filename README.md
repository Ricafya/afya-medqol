# afya-medqol

Cálculo dos índices de qualidade de vida da Afya, a partir das respostas aos
instrumentos. Dois modelos, calibrações independentes, ambos com escoragem
100% determinística (quadratura fixa, sem semente):

- **Afya MedQoL** — médicos formados (13 itens, 3 domínios).
- **IQoL** — estudantes de medicina (8 itens, modelo bifatorial).

Os parâmetros de ambas as calibrações ficam fixos no código-fonte
([`parameters_physician.py`](src/afya_medqol/parameters_physician.py),
[`parameters_student.py`](src/afya_medqol/parameters_student.py)) — não há
leitura de arquivo externo (CSV/Excel) em tempo de execução.

## Instalação

```bash
pip install afya-medqol
```

---

## Afya MedQoL (médicos)

Modelo Samejima GRM (Graded Response Model) tridimensional com escoragem EAP
(Expected A Posteriori). Calibração fixada em **2024_2** (Gobbo Jr M et al.,
*BMJ Open* 2025;15:e102783), com domínios independentes (Σ = I): cada domínio
(F1, F2, F3) funciona como uma régua própria — zerar ou excluir itens de um
domínio não afeta os outros.

| Domínio | Descrição | Itens |
|---|---|---|
| F1 | Qualidade de Vida | 6 itens (`F1_1_enjoymentoflife`, `F1_2_financialsufficiency`, `F1_3_accesstoinformation`, `F1_4_leisureopportunities`, `F1_5_mobilitypast2weeks`, `F1_6_accesstohealthservices`) |
| F2 | Suporte Institucional / Percepção do Trabalho | 4 itens (`F2_1_technicaltraining`, `F2_2_mentalhealthsupport`, `F2_3_coworkersupportnetwork`, `F2_4_educationalhandlingoferrors`) |
| F3 | Estresse Percebido | 3 itens (`F3_1_stresshurtsperformance`, `F3_2_stressledtoerrors`, `F3_3_stresshurtsrelationships`) |

O escore global combina os três domínios (F3 invertido só na composição do
global) com pesos proporcionais à discriminação (Σ\|a\|) de cada fator.

### Uso como biblioteca

```python
import pandas as pd
from afya_medqol import MedQoLCalculator

df_respostas = pd.read_csv("respostas.csv")

calc = MedQoLCalculator()
resultado = calc.calcular(df_respostas)

print(resultado[["theta_global", "T_score_global"]])
```

Para escorar um único respondente:

```python
resultado = calc.score_physician({
    "F1_1_enjoymentoflife": 4,
    "F1_2_financialsufficiency": 3,
    # ... demais itens (ver afya_medqol.ITENS_TODOS)
})
print(resultado["theta_global"], resultado["T_score_global"])
```

`MedQoLCalculator` precomputa a grade de quadratura e as probabilidades por
item uma única vez na construção — reutilize a mesma instância ao escorar
múltiplos lotes.

### Linha de comando

```bash
afya-medqol respostas.csv
afya-medqol respostas.csv --saida resultado.csv
```

### Saída

- `theta_F1`, `theta_F2`, `theta_F3`, `theta_global`
- `T_score_F1`, `T_score_F2`, `T_score_F3`, `T_score_global` (50 + 10·θ)

`score_physician` (respondente único) omite `T_score_F1`, `T_score_F2` e
`T_score_F3` do dicionário retornado — continuam disponíveis via `calcular`.

---

## IQoL (estudantes de medicina)

Modelo GRM **bifatorial** (Samejima): cada um dos 8 itens carrega num fator
geral de qualidade de vida (θ_G, comum a todos os itens) e num fator
específico do seu domínio (θ_S). Fatores ortogonais, prior N(0,1),
escoragem EAP por integração numérica (grade fixa de 121 nós em [-6, 6]).
Reproduz Gobbo M Jr et al., *BMJ Open* 2026;16:e106371 (N=10844).

| Domínio | Descrição | Itens |
|---|---|---|
| 1 | Bem-estar psicológico | `F1_1_overallqol`, `F1_2_satisfactionwithhealth`, `F1_3_enjoymentoflife`, `F1_4_perceivedmeaninginlife` |
| 2 | Vitalidade | `F2_1_energyfordailyactivities`, `F2_2_satisfactionwithsleep` |
| 3 | Capacidade funcional percebida | `F3_1_performdailyactivities`, `F3_2_capacityforwork` |

O escore global é o composto ponderado dos três domínios (pesos 0.494 /
0.172 / 0.335, proporcionais à discriminação de cada fator na calibração).

### Uso como biblioteca

```python
import pandas as pd
from afya_medqol import IQoLCalculator

df_respostas = pd.read_csv("respostas_estudantes.csv")

calc = IQoLCalculator()
resultado = calc.calcular(df_respostas)

print(resultado[["theta_global", "T_score_global"]])
```

Para escorar um único estudante:

```python
resultado = calc.score_student({
    "F1_1_overallqol": 4, "F1_2_satisfactionwithhealth": 4, "F1_3_enjoymentoflife": 4, "F1_4_perceivedmeaninginlife": 3,
    "F2_1_energyfordailyactivities": 3, "F2_2_satisfactionwithsleep": 4, "F3_1_performdailyactivities": 3, "F3_2_capacityforwork": 3,
})
print(resultado["theta_global"], resultado["T_score_global"])
```

### Linha de comando

```bash
iqol-estudante respostas_estudantes.csv
iqol-estudante respostas_estudantes.csv --saida resultado.csv
```

### Saída

- `theta_bem_estar_psicologico`, `theta_vitalidade`, `theta_capacidade_funcional`, `theta_global`
- `T_score_global` (50 + 10·z, z-score do θ_global na amostra de referência)

---

## Licença

Apache License 2.0 — ver [LICENSE](LICENSE).
