# Plano de execução em lotes

**Total de itens:** 678
**Tamanho do lote:** 20
**Quantidade de lotes:** 34
**Último lote:** 18 itens

Cada lote prepara prompts e guias para 20 itens. Não dispara áudio no NotebookLM — somente gera `prompts/<id>.md` e `guias/<id>.md`. Disparo dos áudios é etapa posterior (runner separado).

## Como executar um lote

```bash
cd ~/dev/notebooklm_edson/projetos/cof_v2
python3 scripts/04_generate_prompt_batch.py --batch <N>   # 1..34
```

## Mapa de lotes

| Lote | Itens | Faixa de IDs | Categorias |
|---:|---:|---|---|
| 01 | 20 | `aula-001` … `aula-020` | aula |
| 02 | 20 | `aula-021` … `aula-041` | aula |
| 03 | 20 | `aula-088` … `aula-060` | aula |
| 04 | 20 | `aula-061` … `aula-081` | aula |
| 05 | 20 | `aula-082` … `aula-101` | aula |
| 06 | 20 | `aula-102` … `aula-121` | aula |
| 07 | 20 | `aula-122` … `aula-141` | aula |
| 08 | 20 | `aula-142` … `aula-162` | aula |
| 09 | 20 | `aula-150` … `aula-180` | aula |
| 10 | 20 | `aula-181` … `aula-200` | aula |
| 11 | 20 | `aula-201` … `aula-220` | aula |
| 12 | 20 | `aula-221` … `aula-239` | aula |
| 13 | 20 | `aula-240` … `aula-260` | aula |
| 14 | 20 | `aula-261` … `aula-280` | aula |
| 15 | 20 | `aula-281` … `aula-302` | aula |
| 16 | 20 | `aula-303` … `aula-324` | aula |
| 17 | 20 | `aula-325` … `aula-343` | aula |
| 18 | 20 | `aula-344` … `aula-363` | aula |
| 19 | 20 | `aula-365` … `aula-387` | aula |
| 20 | 20 | `aula-388` … `aula-404` | aula |
| 21 | 20 | `aula-405` … `aula-421` | aula |
| 22 | 20 | `aula-422` … `aula-441` | aula |
| 23 | 20 | `aula-443` … `aula-462` | aula |
| 24 | 20 | `aula-463` … `aula-484` | aula |
| 25 | 20 | `aula-485` … `aula-503` | aula |
| 26 | 20 | `aula-504` … `aula-523` | aula |
| 27 | 20 | `aula-524` … `aula-543` | aula |
| 28 | 20 | `aula-544` … `aula-566` | aula |
| 29 | 20 | `aula-567` … `aula-469` | aula |
| 30 | 20 | `aula-545` … `extra-princ-pios-e-m-todos-da-auto-educa-o` | aula, extracurricular |
| 31 | 20 | `extra-ser-e-poder-princ-pios-e-m-todos-da-ci-ncia-pol-ti` … `livro-como-tornar-se-um-gostos-o-intelectual` | extracurricular, livro |
| 32 | 20 | `livro-como-tornar-se-um-buscador-da-verdade-introdu-o-ze` … `livro-implica-es-para-o-brasil-nos-campos-pol-tico-e-eco` | livro |
| 33 | 20 | `livro-influ-ncias-intelectuais-que-recebi-at-a-d-cada-de` … `livro-o-mundo-exterior-e-as-perguntas-c-pticas` | livro |
| 34 | 18 | `livro-o-que-psique` … `tematica-teoria-estado` | livro, tematica |

## Lotes detalhados

### Lote 01 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-001` | aula | Aula 001 | Deep Dive |
|  2 | `aula-002` | aula | Aula 002 | Deep Dive |
|  3 | `aula-003` | aula | Aula 003 | Deep Dive |
|  4 | `aula-004` | aula | Aula 004 | Deep Dive |
|  5 | `aula-005` | aula | Aula 005 | Deep Dive |
|  6 | `aula-006` | aula | Aula 006 | Deep Dive |
|  7 | `aula-007` | aula | Aula 007 | Deep Dive |
|  8 | `aula-008` | aula | Aula 008 | Deep Dive |
|  9 | `aula-009` | aula | Aula 009 | Deep Dive |
| 10 | `aula-010` | aula | Aula 010 | Deep Dive |
| 11 | `aula-011` | aula | Aula 011 | Deep Dive |
| 12 | `aula-012` | aula | Aula 012 | Deep Dive |
| 13 | `aula-013` | aula | Aula 013 | Deep Dive |
| 14 | `aula-014` | aula | Aula 014 | Deep Dive |
| 15 | `aula-015` | aula | Aula 015 | Deep Dive |
| 16 | `aula-016` | aula | Aula 016 | Deep Dive |
| 17 | `aula-017` | aula | Aula 017 | Deep Dive |
| 18 | `aula-018` | aula | Aula 018 | Deep Dive |
| 19 | `aula-019` | aula | Aula 019 | Deep Dive |
| 20 | `aula-020` | aula | Aula 020 | Deep Dive |

### Lote 02 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-021` | aula | Aula 021 | Deep Dive |
|  2 | `aula-022` | aula | Aula 022 | Deep Dive |
|  3 | `aula-023` | aula | Aula 023 | Deep Dive |
|  4 | `aula-024` | aula | Aula 024 | Deep Dive |
|  5 | `aula-025` | aula | Aula 025 | Deep Dive |
|  6 | `aula-026` | aula | Aula 026 | Deep Dive |
|  7 | `aula-028` | aula | Aula 028 | Deep Dive |
|  8 | `aula-029` | aula | Aula 029 | Deep Dive |
|  9 | `aula-030` | aula | Aula 030 | Deep Dive |
| 10 | `aula-034` | aula | Aula 034 | Deep Dive |
| 11 | `aula-031` | aula | Aula 031 | Deep Dive |
| 12 | `aula-032` | aula | Aula 032 | Deep Dive |
| 13 | `aula-033` | aula | Aula 033 | Deep Dive |
| 14 | `aula-035` | aula | Aula 035 | Deep Dive |
| 15 | `aula-036` | aula | Aula 036 | Deep Dive |
| 16 | `aula-037` | aula | Aula 037 | Deep Dive |
| 17 | `aula-038` | aula | Aula 038 | Deep Dive |
| 18 | `aula-039` | aula | Aula 039 | Deep Dive |
| 19 | `aula-040` | aula | Aula 040 | Deep Dive |
| 20 | `aula-041` | aula | Aula 041 | Deep Dive |

### Lote 03 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-088` | aula | Aula 088 | Deep Dive |
|  2 | `aula-042` | aula | Aula 042 | Deep Dive |
|  3 | `aula-043` | aula | Aula 043 | Deep Dive |
|  4 | `aula-044` | aula | Aula 044 | Deep Dive |
|  5 | `aula-045` | aula | Aula 045 | Deep Dive |
|  6 | `aula-046` | aula | Aula 046 | Deep Dive |
|  7 | `aula-047` | aula | Aula 047 | Deep Dive |
|  8 | `aula-048` | aula | Aula 048 | Deep Dive |
|  9 | `aula-049` | aula | Aula 049 | Deep Dive |
| 10 | `aula-050` | aula | Aula 050 | Deep Dive |
| 11 | `aula-051` | aula | Aula 051 | Deep Dive |
| 12 | `aula-052` | aula | Aula 052 | Deep Dive |
| 13 | `aula-053` | aula | Aula 053 | Deep Dive |
| 14 | `aula-054` | aula | Aula 054 | Deep Dive |
| 15 | `aula-055` | aula | Aula 055 | Deep Dive |
| 16 | `aula-056` | aula | Aula 056 | Deep Dive |
| 17 | `aula-057` | aula | Aula 057 | Deep Dive |
| 18 | `aula-058` | aula | Aula 058 | Deep Dive |
| 19 | `aula-059` | aula | Aula 059 | Deep Dive |
| 20 | `aula-060` | aula | Aula 060 | Deep Dive |

### Lote 04 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-061` | aula | Aula 061 | Deep Dive |
|  2 | `aula-062` | aula | Aula 062 | Deep Dive |
|  3 | `aula-063` | aula | Aula 063 | Deep Dive |
|  4 | `aula-064` | aula | Aula 064 | Deep Dive |
|  5 | `aula-065` | aula | Aula 065 | Deep Dive |
|  6 | `aula-066` | aula | Aula 066 | Deep Dive |
|  7 | `aula-070` | aula | Aula 070 | Deep Dive |
|  8 | `aula-067` | aula | Aula 067 | Deep Dive |
|  9 | `aula-068` | aula | Aula 068 | Deep Dive |
| 10 | `aula-069` | aula | Aula 069 | Deep Dive |
| 11 | `aula-071` | aula | Aula 071 | Deep Dive |
| 12 | `aula-072` | aula | Aula 072 | Deep Dive |
| 13 | `aula-073` | aula | Aula 073 | Deep Dive |
| 14 | `aula-074` | aula | Aula 074 | Deep Dive |
| 15 | `aula-075` | aula | Aula 075 | Deep Dive |
| 16 | `aula-077` | aula | Aula 077 | Deep Dive |
| 17 | `aula-078` | aula | Aula 078 | Deep Dive |
| 18 | `aula-027` | aula | Aula 027 | Deep Dive |
| 19 | `aula-080` | aula | Aula 080 | Deep Dive |
| 20 | `aula-081` | aula | Aula 081 | Deep Dive |

### Lote 05 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-082` | aula | Aula 082 | Deep Dive |
|  2 | `aula-083` | aula | Aula 083 | Deep Dive |
|  3 | `aula-084` | aula | Aula 084 | Deep Dive |
|  4 | `aula-076` | aula | Aula 076 | Deep Dive |
|  5 | `aula-085` | aula | Aula 085 | Deep Dive |
|  6 | `aula-086` | aula | Aula 086 | Deep Dive |
|  7 | `aula-087` | aula | Aula 087 | Deep Dive |
|  8 | `aula-089` | aula | Aula 089 | Deep Dive |
|  9 | `aula-090` | aula | Aula 090 | Deep Dive |
| 10 | `aula-091` | aula | Aula 091 | Deep Dive |
| 11 | `aula-092` | aula | Aula 092 | Deep Dive |
| 12 | `aula-093` | aula | Aula 093 | Deep Dive |
| 13 | `aula-094` | aula | Aula 094 | Deep Dive |
| 14 | `aula-095` | aula | Aula 095 | Deep Dive |
| 15 | `aula-096` | aula | Aula 096 | Deep Dive |
| 16 | `aula-097` | aula | Aula 097 | Deep Dive |
| 17 | `aula-098` | aula | Aula 098 | Deep Dive |
| 18 | `aula-099` | aula | Aula 099 | Deep Dive |
| 19 | `aula-100` | aula | Aula 100 | Deep Dive |
| 20 | `aula-101` | aula | Aula 101 | Deep Dive |

### Lote 06 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-102` | aula | Aula 102 | Deep Dive |
|  2 | `aula-103` | aula | Aula 103 | Deep Dive |
|  3 | `aula-104` | aula | Aula 104 | Deep Dive |
|  4 | `aula-106` | aula | Aula 106 | Deep Dive |
|  5 | `aula-105` | aula | Aula 105 | Deep Dive |
|  6 | `aula-107` | aula | Aula 107 | Deep Dive |
|  7 | `aula-108` | aula | Aula 108 | Deep Dive |
|  8 | `aula-109` | aula | Aula 109 | Deep Dive |
|  9 | `aula-110` | aula | Aula 110 | Deep Dive |
| 10 | `aula-115` | aula | Aula 115 | Deep Dive |
| 11 | `aula-111` | aula | Aula 111 | Deep Dive |
| 12 | `aula-112` | aula | Aula 112 | Deep Dive |
| 13 | `aula-113` | aula | Aula 113 | Deep Dive |
| 14 | `aula-114` | aula | Aula 114 | Deep Dive |
| 15 | `aula-116` | aula | Aula 116 | Deep Dive |
| 16 | `aula-117` | aula | Aula 117 | Deep Dive |
| 17 | `aula-118` | aula | Aula 118 | Deep Dive |
| 18 | `aula-119` | aula | Aula 119 | Deep Dive |
| 19 | `aula-120` | aula | Aula 120 | Deep Dive |
| 20 | `aula-121` | aula | Aula 121 | Deep Dive |

### Lote 07 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-122` | aula | Aula 122 | Deep Dive |
|  2 | `aula-123` | aula | Aula 123 | Deep Dive |
|  3 | `aula-124` | aula | Aula 124 | Deep Dive |
|  4 | `aula-125` | aula | Aula 125 | Deep Dive |
|  5 | `aula-126` | aula | Aula 126 | Deep Dive |
|  6 | `aula-127` | aula | Aula 127 | Deep Dive |
|  7 | `aula-128` | aula | Aula 128 | Deep Dive |
|  8 | `aula-129` | aula | Aula 129 | Deep Dive |
|  9 | `aula-130` | aula | Aula 130 | Deep Dive |
| 10 | `aula-131` | aula | Aula 131 | Deep Dive |
| 11 | `aula-132` | aula | Aula 132 | Deep Dive |
| 12 | `aula-133` | aula | Aula 133 | Deep Dive |
| 13 | `aula-134` | aula | Aula 134 | Deep Dive |
| 14 | `aula-135` | aula | Aula 135 | Deep Dive |
| 15 | `aula-136` | aula | Aula 136 | Deep Dive |
| 16 | `aula-137` | aula | Aula 137 | Deep Dive |
| 17 | `aula-138` | aula | Aula 138 | Deep Dive |
| 18 | `aula-139` | aula | Aula 139 | Deep Dive |
| 19 | `aula-140` | aula | Aula 140 | Deep Dive |
| 20 | `aula-141` | aula | Aula 141 | Deep Dive |

### Lote 08 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-142` | aula | Aula 142 | Deep Dive |
|  2 | `aula-143` | aula | Aula 143 | Deep Dive |
|  3 | `aula-144` | aula | Aula 144 | Deep Dive |
|  4 | `aula-145` | aula | Aula 145 | Deep Dive |
|  5 | `aula-146` | aula | Aula 146 | Deep Dive |
|  6 | `aula-147` | aula | Aula 147 | Deep Dive |
|  7 | `aula-148` | aula | Aula 148 | Deep Dive |
|  8 | `aula-151` | aula | Aula 151 | Deep Dive |
|  9 | `aula-152` | aula | Aula 152 | Deep Dive |
| 10 | `aula-153` | aula | Aula 153 | Deep Dive |
| 11 | `aula-154` | aula | Aula 154 | Deep Dive |
| 12 | `aula-155` | aula | Aula 155 | Deep Dive |
| 13 | `aula-156` | aula | Aula 156 | Deep Dive |
| 14 | `aula-157` | aula | Aula 157 | Deep Dive |
| 15 | `aula-158` | aula | Aula 158 | Deep Dive |
| 16 | `aula-159` | aula | Aula 159 | Deep Dive |
| 17 | `aula-160` | aula | Aula 160 | Deep Dive |
| 18 | `aula-161` | aula | Aula 161 | Deep Dive |
| 19 | `aula-149` | aula | Aula 149 | Deep Dive |
| 20 | `aula-162` | aula | Aula 162 | Deep Dive |

### Lote 09 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-150` | aula | Aula 150 | Deep Dive |
|  2 | `aula-163` | aula | Aula 163 | Deep Dive |
|  3 | `aula-164` | aula | Aula 164 | Deep Dive |
|  4 | `aula-165` | aula | Aula 165 | Deep Dive |
|  5 | `aula-166` | aula | Aula 166 | Deep Dive |
|  6 | `aula-167` | aula | Aula 167 | Deep Dive |
|  7 | `aula-168` | aula | Aula 168 | Deep Dive |
|  8 | `aula-169` | aula | Aula 169 | Deep Dive |
|  9 | `aula-170` | aula | Aula 170 | Deep Dive |
| 10 | `aula-171` | aula | Aula 171 | Deep Dive |
| 11 | `aula-176` | aula | Aula 176 | Deep Dive |
| 12 | `aula-172` | aula | Aula 172 | Deep Dive |
| 13 | `aula-173` | aula | Aula 173 | Deep Dive |
| 14 | `aula-174` | aula | Aula 174 | Deep Dive |
| 15 | `aula-175` | aula | Aula 175 | Deep Dive |
| 16 | `aula-079` | aula | Aula 079 | Deep Dive |
| 17 | `aula-177` | aula | Aula 177 | Deep Dive |
| 18 | `aula-178` | aula | Aula 178 | Deep Dive |
| 19 | `aula-179` | aula | Aula 179 | Deep Dive |
| 20 | `aula-180` | aula | Aula 180 | Deep Dive |

### Lote 10 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-181` | aula | Aula 181 | Deep Dive |
|  2 | `aula-182` | aula | Aula 182 | Deep Dive |
|  3 | `aula-183` | aula | Aula 183 | Deep Dive |
|  4 | `aula-184` | aula | Aula 184 | Deep Dive |
|  5 | `aula-185` | aula | Aula 185 | Deep Dive |
|  6 | `aula-186` | aula | Aula 186 | Deep Dive |
|  7 | `aula-187` | aula | Aula 187 | Deep Dive |
|  8 | `aula-188` | aula | Aula 188 | Deep Dive |
|  9 | `aula-189` | aula | Aula 189 | Deep Dive |
| 10 | `aula-190` | aula | Aula 190 | Deep Dive |
| 11 | `aula-191` | aula | Aula 191 | Deep Dive |
| 12 | `aula-192` | aula | Aula 192 | Deep Dive |
| 13 | `aula-193` | aula | Aula 193 | Deep Dive |
| 14 | `aula-194` | aula | Aula 194 | Deep Dive |
| 15 | `aula-195` | aula | Aula 195 | Deep Dive |
| 16 | `aula-196` | aula | Aula 196 | Deep Dive |
| 17 | `aula-197` | aula | Aula 197 | Deep Dive |
| 18 | `aula-198` | aula | Aula 198 | Deep Dive |
| 19 | `aula-199` | aula | Aula 199 | Deep Dive |
| 20 | `aula-200` | aula | Aula 200 | Deep Dive |

### Lote 11 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-201` | aula | Aula 201 | Deep Dive |
|  2 | `aula-202` | aula | Aula 202 | Deep Dive |
|  3 | `aula-203` | aula | Aula 203 | Deep Dive |
|  4 | `aula-204` | aula | Aula 204 | Deep Dive |
|  5 | `aula-205` | aula | Aula 205 | Deep Dive |
|  6 | `aula-206` | aula | Aula 206 | Deep Dive |
|  7 | `aula-207` | aula | Aula 207 | Deep Dive |
|  8 | `aula-208` | aula | Aula 208 | Deep Dive |
|  9 | `aula-209` | aula | Aula 209 | Deep Dive |
| 10 | `aula-210` | aula | Aula 210 | Deep Dive |
| 11 | `aula-211` | aula | Aula 211 | Deep Dive |
| 12 | `aula-212` | aula | Aula 212 | Deep Dive |
| 13 | `aula-213` | aula | Aula 213 | Deep Dive |
| 14 | `aula-214` | aula | Aula 214 | Deep Dive |
| 15 | `aula-215` | aula | Aula 215 | The Brief |
| 16 | `aula-216` | aula | Aula 216 | Deep Dive |
| 17 | `aula-217` | aula | Aula 217 | Deep Dive |
| 18 | `aula-218` | aula | Aula 218 | Deep Dive |
| 19 | `aula-219` | aula | Aula 219 | Deep Dive |
| 20 | `aula-220` | aula | Aula 220 | Deep Dive |

### Lote 12 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-221` | aula | Aula 221 | Deep Dive |
|  2 | `aula-222` | aula | Aula 222 | Deep Dive |
|  3 | `aula-223` | aula | Aula 223 | Deep Dive |
|  4 | `aula-224` | aula | Aula 224 | Deep Dive |
|  5 | `aula-225` | aula | Aula 225 | Deep Dive |
|  6 | `aula-226` | aula | Aula 226 | Deep Dive |
|  7 | `aula-227` | aula | Aula 227 | Deep Dive |
|  8 | `aula-228` | aula | Aula 228 | Deep Dive |
|  9 | `aula-229` | aula | Aula 229 | Deep Dive |
| 10 | `aula-230` | aula | Aula 230 | Deep Dive |
| 11 | `aula-231` | aula | Aula 231 | Deep Dive |
| 12 | `aula-232` | aula | Aula 232 | Deep Dive |
| 13 | `aula-233` | aula | Aula 233 | Deep Dive |
| 14 | `aula-234` | aula | Aula 234 | Deep Dive |
| 15 | `aula-235` | aula | Aula 235 | Deep Dive |
| 16 | `aula-236` | aula | Aula 236 | Deep Dive |
| 17 | `aula-237` | aula | Aula 237 | Deep Dive |
| 18 | `aula-238` | aula | Aula 238 | Deep Dive |
| 19 | `aula-282` | aula | Aula 282 | Deep Dive |
| 20 | `aula-239` | aula | Aula 239 | Deep Dive |

### Lote 13 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-240` | aula | Aula 240 | Deep Dive |
|  2 | `aula-241` | aula | Aula 241 | Deep Dive |
|  3 | `aula-242` | aula | Aula 242 | Deep Dive |
|  4 | `aula-243` | aula | Aula 243 | Deep Dive |
|  5 | `aula-244` | aula | Aula 244 | Deep Dive |
|  6 | `aula-245` | aula | Aula 245 | Deep Dive |
|  7 | `aula-246` | aula | Aula 246 | Deep Dive |
|  8 | `aula-247` | aula | Aula 247 | Deep Dive |
|  9 | `aula-248` | aula | Aula 248 | Deep Dive |
| 10 | `aula-249` | aula | Aula 249 | Deep Dive |
| 11 | `aula-250` | aula | Aula 250 | Deep Dive |
| 12 | `aula-251` | aula | Aula 251 | Deep Dive |
| 13 | `aula-252` | aula | Aula 252 | Deep Dive |
| 14 | `aula-253` | aula | Aula 253 | Deep Dive |
| 15 | `aula-254` | aula | Aula 254 | Deep Dive |
| 16 | `aula-255` | aula | Aula 255 | Deep Dive |
| 17 | `aula-256` | aula | Aula 256 | Deep Dive |
| 18 | `aula-257` | aula | Aula 257 | Deep Dive |
| 19 | `aula-258` | aula | Aula 258 | Deep Dive |
| 20 | `aula-260` | aula | Aula 260 | Deep Dive |

### Lote 14 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-261` | aula | Aula 261 | Deep Dive |
|  2 | `aula-262` | aula | Aula 262 | Deep Dive |
|  3 | `aula-259` | aula | Aula 259 | Deep Dive |
|  4 | `aula-263` | aula | Aula 263 | Deep Dive |
|  5 | `aula-264` | aula | Aula 264 | Deep Dive |
|  6 | `aula-265` | aula | Aula 265 | Deep Dive |
|  7 | `aula-266` | aula | Aula 266 | Deep Dive |
|  8 | `aula-267` | aula | Aula 267 | Deep Dive |
|  9 | `aula-268` | aula | Aula 268 | Deep Dive |
| 10 | `aula-269` | aula | Aula 269 | Deep Dive |
| 11 | `aula-270` | aula | Aula 270 | Deep Dive |
| 12 | `aula-271` | aula | Aula 271 | Deep Dive |
| 13 | `aula-272` | aula | Aula 272 | Deep Dive |
| 14 | `aula-273` | aula | Aula 273 | Deep Dive |
| 15 | `aula-274` | aula | Aula 274 | Deep Dive |
| 16 | `aula-275` | aula | Aula 275 | Deep Dive |
| 17 | `aula-276` | aula | Aula 276 | Deep Dive |
| 18 | `aula-277` | aula | Aula 277 | Deep Dive |
| 19 | `aula-279` | aula | Aula 279 | Deep Dive |
| 20 | `aula-280` | aula | Aula 280 | Deep Dive |

### Lote 15 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-281` | aula | Aula 281 | Deep Dive |
|  2 | `aula-283` | aula | Aula 283 | Deep Dive |
|  3 | `aula-284` | aula | Aula 284 | Deep Dive |
|  4 | `aula-285` | aula | Aula 285 | Deep Dive |
|  5 | `aula-286` | aula | Aula 286 | Deep Dive |
|  6 | `aula-287` | aula | Aula 287 | Deep Dive |
|  7 | `aula-289` | aula | Aula 289 | Deep Dive |
|  8 | `aula-290` | aula | Aula 290 | Deep Dive |
|  9 | `aula-291` | aula | Aula 291 | Deep Dive |
| 10 | `aula-292` | aula | Aula 292 | Deep Dive |
| 11 | `aula-293` | aula | Aula 293 | Deep Dive |
| 12 | `aula-294` | aula | Aula 294 | Deep Dive |
| 13 | `aula-295` | aula | Aula 295 | Deep Dive |
| 14 | `aula-296` | aula | Aula 296 | Deep Dive |
| 15 | `aula-297` | aula | Aula 297 | Deep Dive |
| 16 | `aula-298` | aula | Aula 298 | Deep Dive |
| 17 | `aula-299` | aula | Aula 299 | Deep Dive |
| 18 | `aula-300` | aula | Aula 300 | Deep Dive |
| 19 | `aula-301` | aula | Aula 301 | Deep Dive |
| 20 | `aula-302` | aula | Aula 302 | Deep Dive |

### Lote 16 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-303` | aula | Aula 303 | Deep Dive |
|  2 | `aula-304` | aula | Aula 304 | Deep Dive |
|  3 | `aula-306` | aula | Aula 306 | Deep Dive |
|  4 | `aula-278` | aula | Aula 278 | Deep Dive |
|  5 | `aula-307` | aula | Aula 307 | Deep Dive |
|  6 | `aula-308` | aula | Aula 308 | Deep Dive |
|  7 | `aula-309` | aula | Aula 309 | Deep Dive |
|  8 | `aula-310` | aula | Aula 310 | Deep Dive |
|  9 | `aula-311` | aula | Aula 311 | Deep Dive |
| 10 | `aula-312` | aula | Aula 312 | Deep Dive |
| 11 | `aula-315` | aula | Aula 315 | Deep Dive |
| 12 | `aula-316` | aula | Aula 316 | Deep Dive |
| 13 | `aula-317` | aula | Aula 317 | Deep Dive |
| 14 | `aula-318` | aula | Aula 318 | Deep Dive |
| 15 | `aula-319` | aula | Aula 319 | Deep Dive |
| 16 | `aula-320` | aula | Aula 320 | Deep Dive |
| 17 | `aula-321` | aula | Aula 321 | Deep Dive |
| 18 | `aula-322` | aula | Aula 322 | Deep Dive |
| 19 | `aula-323` | aula | Aula 323 | Deep Dive |
| 20 | `aula-324` | aula | Aula 324 | Deep Dive |

### Lote 17 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-325` | aula | Aula 325 | Deep Dive |
|  2 | `aula-326` | aula | Aula 326 | Deep Dive |
|  3 | `aula-327` | aula | Aula 327 | Deep Dive |
|  4 | `aula-328` | aula | Aula 328 | Deep Dive |
|  5 | `aula-329` | aula | Aula 329 | Deep Dive |
|  6 | `aula-330` | aula | Aula 330 | Deep Dive |
|  7 | `aula-331` | aula | Aula 331 | Deep Dive |
|  8 | `aula-332` | aula | Aula 332 | Deep Dive |
|  9 | `aula-333` | aula | Aula 333 | Deep Dive |
| 10 | `aula-335` | aula | Aula 335 | Deep Dive |
| 11 | `aula-336` | aula | Aula 336 | Deep Dive |
| 12 | `aula-337` | aula | Aula 337 | Deep Dive |
| 13 | `aula-334` | aula | Aula 334 | Deep Dive |
| 14 | `aula-384` | aula | Aula 384 | Deep Dive |
| 15 | `aula-338` | aula | Aula 338 | Deep Dive |
| 16 | `aula-339` | aula | Aula 339 | Deep Dive |
| 17 | `aula-340` | aula | Aula 340 | Deep Dive |
| 18 | `aula-341` | aula | Aula 341 | Deep Dive |
| 19 | `aula-342` | aula | Aula 342 | Deep Dive |
| 20 | `aula-343` | aula | Aula 343 | Deep Dive |

### Lote 18 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-344` | aula | Aula 344 | Deep Dive |
|  2 | `aula-345` | aula | Aula 345 | Deep Dive |
|  3 | `aula-346` | aula | Aula 346 | Deep Dive |
|  4 | `aula-347` | aula | Aula 347 | Deep Dive |
|  5 | `aula-348` | aula | Aula 348 | Deep Dive |
|  6 | `aula-349` | aula | Aula 349 | Deep Dive |
|  7 | `aula-350` | aula | Aula 350 | Deep Dive |
|  8 | `aula-351` | aula | Aula 351 | Deep Dive |
|  9 | `aula-352` | aula | Aula 352 | Deep Dive |
| 10 | `aula-353` | aula | Aula 353 | Deep Dive |
| 11 | `aula-355` | aula | Aula 355 | Deep Dive |
| 12 | `aula-357` | aula | Aula 357 | Deep Dive |
| 13 | `aula-358` | aula | Aula 358 | Deep Dive |
| 14 | `aula-354` | aula | Aula 354 | Deep Dive |
| 15 | `aula-356` | aula | Aula 356 | Deep Dive |
| 16 | `aula-359` | aula | Aula 359 | Deep Dive |
| 17 | `aula-360` | aula | Aula 360 | Deep Dive |
| 18 | `aula-361` | aula | Aula 361 | Deep Dive |
| 19 | `aula-362` | aula | Aula 362 | Deep Dive |
| 20 | `aula-363` | aula | Aula 363 | Deep Dive |

### Lote 19 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-365` | aula | Aula 365 | Deep Dive |
|  2 | `aula-367` | aula | Aula 367 | Deep Dive |
|  3 | `aula-368` | aula | Aula 368 | Deep Dive |
|  4 | `aula-369` | aula | Aula 369 | Deep Dive |
|  5 | `aula-413` | aula | Aula 413 | The Brief |
|  6 | `aula-370` | aula | Aula 370 | Deep Dive |
|  7 | `aula-372` | aula | Aula 372 | Deep Dive |
|  8 | `aula-373` | aula | Aula 373 | Deep Dive |
|  9 | `aula-374` | aula | Aula 374 | Deep Dive |
| 10 | `aula-375` | aula | Aula 375 | Deep Dive |
| 11 | `aula-376` | aula | Aula 376 | Deep Dive |
| 12 | `aula-377` | aula | Aula 377 | Deep Dive |
| 13 | `aula-378` | aula | Aula 378 | Deep Dive |
| 14 | `aula-379` | aula | Aula 379 | Deep Dive |
| 15 | `aula-380` | aula | Aula 380 | Deep Dive |
| 16 | `aula-381` | aula | Aula 381 | Deep Dive |
| 17 | `aula-382` | aula | Aula 382 | Deep Dive |
| 18 | `aula-385` | aula | Aula 385 | Deep Dive |
| 19 | `aula-386` | aula | Aula 386 | Deep Dive |
| 20 | `aula-387` | aula | Aula 387 | Deep Dive |

### Lote 20 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-388` | aula | Aula 388 | Deep Dive |
|  2 | `aula-389` | aula | Aula 389 | Deep Dive |
|  3 | `aula-390` | aula | Aula 390 | Deep Dive |
|  4 | `aula-392` | aula | Aula 392 | Deep Dive |
|  5 | `aula-393` | aula | Aula 393 | Deep Dive |
|  6 | `aula-394` | aula | Aula 394 | Deep Dive |
|  7 | `aula-395` | aula | Aula 395 | Deep Dive |
|  8 | `aula-391` | aula | Aula 391 | Deep Dive |
|  9 | `aula-396` | aula | Aula 396 | Deep Dive |
| 10 | `aula-397` | aula | Aula 397 | Deep Dive |
| 11 | `aula-398` | aula | Aula 398 | Deep Dive |
| 12 | `aula-305` | aula | Aula 305 | Deep Dive |
| 13 | `aula-399` | aula | Aula 399 | Deep Dive |
| 14 | `aula-400` | aula | Aula 400 | Deep Dive |
| 15 | `aula-401` | aula | Aula 401 | Deep Dive |
| 16 | `aula-406` | aula | Aula 406 | Deep Dive |
| 17 | `aula-402` | aula | Aula 402 | Deep Dive |
| 18 | `aula-442` | aula | Aula 442 | Deep Dive |
| 19 | `aula-403` | aula | Aula 403 | Deep Dive |
| 20 | `aula-404` | aula | Aula 404 | Deep Dive |

### Lote 21 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-405` | aula | Aula 405 | Deep Dive |
|  2 | `aula-313` | aula | Aula 313 | Deep Dive |
|  3 | `aula-314` | aula | Aula 314 | Deep Dive |
|  4 | `aula-407` | aula | Aula 407 | Deep Dive |
|  5 | `aula-408` | aula | Aula 408 | Deep Dive |
|  6 | `aula-364` | aula | Aula 364 | Deep Dive |
|  7 | `aula-409` | aula | Aula 409 | Deep Dive |
|  8 | `aula-410` | aula | Aula 410 | Deep Dive |
|  9 | `aula-411` | aula | Aula 411 | Deep Dive |
| 10 | `aula-366` | aula | Aula 366 | Deep Dive |
| 11 | `aula-412` | aula | Aula 412 | Deep Dive |
| 12 | `aula-455` | aula | Aula 455 | Deep Dive |
| 13 | `aula-414` | aula | Aula 414 | Deep Dive |
| 14 | `aula-415` | aula | Aula 415 | Deep Dive |
| 15 | `aula-416` | aula | Aula 416 | Deep Dive |
| 16 | `aula-417` | aula | Aula 417 | Deep Dive |
| 17 | `aula-418` | aula | Aula 418 | Deep Dive |
| 18 | `aula-419` | aula | Aula 419 | Deep Dive |
| 19 | `aula-420` | aula | Aula 420 | Deep Dive |
| 20 | `aula-421` | aula | Aula 421 | Deep Dive |

### Lote 22 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-422` | aula | Aula 422 | Deep Dive |
|  2 | `aula-423` | aula | Aula 423 | Deep Dive |
|  3 | `aula-424` | aula | Aula 424 | Deep Dive |
|  4 | `aula-425` | aula | Aula 425 | Deep Dive |
|  5 | `aula-426` | aula | Aula 426 | Deep Dive |
|  6 | `aula-427` | aula | Aula 427 | Deep Dive |
|  7 | `aula-428` | aula | Aula 428 | Deep Dive |
|  8 | `aula-429` | aula | Aula 429 | Deep Dive |
|  9 | `aula-430` | aula | Aula 430 | Deep Dive |
| 10 | `aula-431` | aula | Aula 431 | Deep Dive |
| 11 | `aula-432` | aula | Aula 432 | Deep Dive |
| 12 | `aula-433` | aula | Aula 433 | Deep Dive |
| 13 | `aula-434` | aula | Aula 434 | Deep Dive |
| 14 | `aula-435` | aula | Aula 435 | Deep Dive |
| 15 | `aula-436` | aula | Aula 436 | Deep Dive |
| 16 | `aula-437` | aula | Aula 437 | Deep Dive |
| 17 | `aula-438` | aula | Aula 438 | Deep Dive |
| 18 | `aula-439` | aula | Aula 439 | Deep Dive |
| 19 | `aula-440` | aula | Aula 440 | Deep Dive |
| 20 | `aula-441` | aula | Aula 441 | Deep Dive |

### Lote 23 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-443` | aula | Aula 443 | Deep Dive |
|  2 | `aula-444` | aula | Aula 444 | Deep Dive |
|  3 | `aula-445` | aula | Aula 445 | Deep Dive |
|  4 | `aula-446` | aula | Aula 446 | Deep Dive |
|  5 | `aula-447` | aula | Aula 447 | Deep Dive |
|  6 | `aula-448` | aula | Aula 448 | Deep Dive |
|  7 | `aula-449` | aula | Aula 449 | Deep Dive |
|  8 | `aula-450` | aula | Aula 450 | Deep Dive |
|  9 | `aula-451` | aula | Aula 451 | Deep Dive |
| 10 | `aula-453` | aula | Aula 453 | Deep Dive |
| 11 | `aula-454` | aula | Aula 454 | Deep Dive |
| 12 | `aula-456` | aula | Aula 456 | Deep Dive |
| 13 | `aula-457` | aula | Aula 457 | The Brief |
| 14 | `aula-371` | aula | Aula 371 | Deep Dive |
| 15 | `aula-471` | aula | Aula 471 | Deep Dive |
| 16 | `aula-458` | aula | Aula 458 | Deep Dive |
| 17 | `aula-459` | aula | Aula 459 | Deep Dive |
| 18 | `aula-460` | aula | Aula 460 | The Brief |
| 19 | `aula-461` | aula | Aula 461 | Deep Dive |
| 20 | `aula-462` | aula | Aula 462 | Deep Dive |

### Lote 24 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-463` | aula | Aula 463 | Deep Dive |
|  2 | `aula-464` | aula | Aula 464 | Deep Dive |
|  3 | `aula-465` | aula | Aula 465 | Deep Dive |
|  4 | `aula-466` | aula | Aula 466 | Deep Dive |
|  5 | `aula-467` | aula | Aula 467 | Deep Dive |
|  6 | `aula-468` | aula | Aula 468 | Deep Dive |
|  7 | `aula-470` | aula | Aula 470 | Deep Dive |
|  8 | `aula-472` | aula | Aula 472 | Deep Dive |
|  9 | `aula-473` | aula | Aula 473 | Deep Dive |
| 10 | `aula-474` | aula | Aula 474 | Deep Dive |
| 11 | `aula-475` | aula | Aula 475 | Deep Dive |
| 12 | `aula-476` | aula | Aula 476 | Deep Dive |
| 13 | `aula-477` | aula | Aula 477 | Deep Dive |
| 14 | `aula-478` | aula | Aula 478 | Deep Dive |
| 15 | `aula-479` | aula | Aula 479 | Deep Dive |
| 16 | `aula-480` | aula | Aula 480 | Deep Dive |
| 17 | `aula-481` | aula | Aula 481 | Deep Dive |
| 18 | `aula-482` | aula | Aula 482 | Deep Dive |
| 19 | `aula-483` | aula | Aula 483 | Deep Dive |
| 20 | `aula-484` | aula | Aula 484 | Deep Dive |

### Lote 25 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-485` | aula | Aula 485 | Deep Dive |
|  2 | `aula-486` | aula | Aula 486 | Deep Dive |
|  3 | `aula-487` | aula | Aula 487 | Deep Dive |
|  4 | `aula-488` | aula | Aula 488 | Deep Dive |
|  5 | `aula-489` | aula | Aula 489 | Deep Dive |
|  6 | `aula-490` | aula | Aula 490 | Deep Dive |
|  7 | `aula-491` | aula | Aula 491 | Deep Dive |
|  8 | `aula-492` | aula | Aula 492 | The Brief |
|  9 | `aula-493` | aula | Aula 493 | The Brief |
| 10 | `aula-494` | aula | Aula 494 | Deep Dive |
| 11 | `aula-495` | aula | Aula 495 | Deep Dive |
| 12 | `aula-496` | aula | Aula 496 | Deep Dive |
| 13 | `aula-497` | aula | Aula 497 | Deep Dive |
| 14 | `aula-498` | aula | Aula 498 | Deep Dive |
| 15 | `aula-499` | aula | Aula 499 | Deep Dive |
| 16 | `aula-500` | aula | Aula 500 | Deep Dive |
| 17 | `aula-501` | aula | Aula 501 | Deep Dive |
| 18 | `aula-550` | aula | Aula 550 | Deep Dive |
| 19 | `aula-502` | aula | Aula 502 | Deep Dive |
| 20 | `aula-503` | aula | Aula 503 | Deep Dive |

### Lote 26 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-504` | aula | Aula 504 | Deep Dive |
|  2 | `aula-505` | aula | Aula 505 | Deep Dive |
|  3 | `aula-506` | aula | Aula 506 | Deep Dive |
|  4 | `aula-508` | aula | Aula 508 | Deep Dive |
|  5 | `aula-509` | aula | Aula 509 | Deep Dive |
|  6 | `aula-510` | aula | Aula 510 | Deep Dive |
|  7 | `aula-511` | aula | Aula 511 | Deep Dive |
|  8 | `aula-507` | aula | Aula 507 | Deep Dive |
|  9 | `aula-512` | aula | Aula 512 | Deep Dive |
| 10 | `aula-513` | aula | Aula 513 | Deep Dive |
| 11 | `aula-514` | aula | Aula 514 | Deep Dive |
| 12 | `aula-515` | aula | Aula 515 | Deep Dive |
| 13 | `aula-516` | aula | Aula 516 | Deep Dive |
| 14 | `aula-517` | aula | Aula 517 | Deep Dive |
| 15 | `aula-518` | aula | Aula 518 | Deep Dive |
| 16 | `aula-519` | aula | Aula 519 | Deep Dive |
| 17 | `aula-520` | aula | Aula 520 | Deep Dive |
| 18 | `aula-521` | aula | Aula 521 | The Brief |
| 19 | `aula-522` | aula | Aula 522 | Deep Dive |
| 20 | `aula-523` | aula | Aula 523 | Deep Dive |

### Lote 27 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-524` | aula | Aula 524 | Deep Dive |
|  2 | `aula-526` | aula | Aula 526 | Deep Dive |
|  3 | `aula-527` | aula | Aula 527 | Deep Dive |
|  4 | `aula-528` | aula | Aula 528 | Deep Dive |
|  5 | `aula-538` | aula | Aula 538 | Deep Dive |
|  6 | `aula-529` | aula | Aula 529 | Deep Dive |
|  7 | `aula-530` | aula | Aula 530 | Deep Dive |
|  8 | `aula-531` | aula | Aula 531 | Deep Dive |
|  9 | `aula-532` | aula | Aula 532 | Deep Dive |
| 10 | `aula-525` | aula | Aula 525 | Deep Dive |
| 11 | `aula-533` | aula | Aula 533 | Deep Dive |
| 12 | `aula-534` | aula | Aula 534 | Deep Dive |
| 13 | `aula-535` | aula | Aula 535 | Deep Dive |
| 14 | `aula-536` | aula | Aula 536 | Deep Dive |
| 15 | `aula-537` | aula | Aula 537 | Deep Dive |
| 16 | `aula-539` | aula | Aula 539 | Deep Dive |
| 17 | `aula-540` | aula | Aula 540 | Deep Dive |
| 18 | `aula-541` | aula | Aula 541 | Deep Dive |
| 19 | `aula-542` | aula | Aula 542 | Deep Dive |
| 20 | `aula-543` | aula | Aula 543 | Deep Dive |

### Lote 28 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-544` | aula | Aula 544 | Deep Dive |
|  2 | `aula-546` | aula | Aula 546 | Deep Dive |
|  3 | `aula-547` | aula | Aula 547 | Deep Dive |
|  4 | `aula-548` | aula | Aula 548 | Deep Dive |
|  5 | `aula-549` | aula | Aula 549 | Deep Dive |
|  6 | `aula-551` | aula | Aula 551 | Deep Dive |
|  7 | `aula-552` | aula | Aula 552 | Deep Dive |
|  8 | `aula-554` | aula | Aula 554 | Deep Dive |
|  9 | `aula-555` | aula | Aula 555 | Deep Dive |
| 10 | `aula-556` | aula | Aula 556 | Deep Dive |
| 11 | `aula-557` | aula | Aula 557 | Deep Dive |
| 12 | `aula-558` | aula | Aula 558 | Deep Dive |
| 13 | `aula-559` | aula | Aula 559 | Deep Dive |
| 14 | `aula-560` | aula | Aula 560 | Deep Dive |
| 15 | `aula-561` | aula | Aula 561 | Deep Dive |
| 16 | `aula-562` | aula | Aula 562 | Deep Dive |
| 17 | `aula-563` | aula | Aula 563 | Deep Dive |
| 18 | `aula-564` | aula | Aula 564 | Deep Dive |
| 19 | `aula-565` | aula | Aula 565 | The Brief |
| 20 | `aula-566` | aula | Aula 566 | The Brief |

### Lote 29 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-567` | aula | Aula 567 | The Brief |
|  2 | `aula-568` | aula | Aula 568 | Deep Dive |
|  3 | `aula-569` | aula | Aula 569 | Deep Dive |
|  4 | `aula-570` | aula | Aula 570 | Deep Dive |
|  5 | `aula-571` | aula | Aula 571 | Deep Dive |
|  6 | `aula-572` | aula | Aula 572 | Deep Dive |
|  7 | `aula-573` | aula | Aula 573 | Deep Dive |
|  8 | `aula-574` | aula | Aula 574 | Deep Dive |
|  9 | `aula-575` | aula | Aula 575 | Deep Dive |
| 10 | `aula-576` | aula | Aula 576 | Deep Dive |
| 11 | `aula-577` | aula | Aula 577 | Deep Dive |
| 12 | `aula-578` | aula | Aula 578 | Deep Dive |
| 13 | `aula-579` | aula | Aula 579 | Deep Dive |
| 14 | `aula-580` | aula | Aula 580 | The Brief |
| 15 | `aula-581` | aula | Aula 581 | Deep Dive |
| 16 | `aula-582` | aula | Aula 582 | Deep Dive |
| 17 | `aula-583` | aula | Aula 583 | Deep Dive |
| 18 | `aula-584` | aula | Aula 584 | Deep Dive |
| 19 | `aula-585` | aula | Aula 585 | Deep Dive |
| 20 | `aula-469` | aula | Aula 469 | Deep Dive |

### Lote 30 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `aula-545` | aula | Aula 545 | The Brief |
|  2 | `extra-a-guerra-contra-a-intelig-ncia-o-que-est-o-fazendo` | extracurricular | A Guerra Contra a Inteligência o que estão fazendo para imbecilizar você | The Critique |
|  3 | `extra-a-crise-da-intelig-ncia-segundo-roger-scruton` | extracurricular | A crise da inteligência segundo Roger Scruton | Deep Dive |
|  4 | `extra-a-forma-o-da-personalidade` | extracurricular | A formação da personalidade | Deep Dive |
|  5 | `extra-as-ra-zes-da-modernidade` | extracurricular | As raízes da modernidade | The Critique |
|  6 | `extra-ci-ncia-pol-tica-saber-prever-e-poder` | extracurricular | Ciência Política Saber, Prever e Poder | The Debate |
|  7 | `extra-como-tornar-se-um-leitor-inteligente` | extracurricular | Como tornar-se um leitor inteligente | Deep Dive |
|  8 | `extra-conceitos-fundamentais-de-psicologia` | extracurricular | Conceitos fundamentais de psicologia | Deep Dive |
|  9 | `extra-conhecimento-e-moralidade` | extracurricular | Conhecimento e moralidade | Deep Dive |
| 10 | `extra-consci-ncia-de-imortalidade` | extracurricular | Consciência de imortalidade | Deep Dive |
| 11 | `extra-esoterismo-na-hist-ria-e-hoje-em-dia` | extracurricular | Esoterismo na História e hoje em dia | Deep Dive |
| 12 | `extra-filosofia-da-ci-ncia` | extracurricular | Filosofia da ciência | Deep Dive |
| 13 | `extra-guerra-cultural-hist-ria-e-estrat-gias` | extracurricular | Guerra Cultural história e estratégias | The Debate |
| 14 | `extra-ii-encontro-de-escritores-brasileiros-na-virginia` | extracurricular | II Encontro de Escritores Brasileiros na Virginia | The Debate |
| 15 | `extra-introdu-o-ao-m-todo-filos-fico` | extracurricular | Introdução ao método filosófico | The Brief |
| 16 | `extra-introdu-o-filosofia-de-eric-voegelin` | extracurricular | Introdução à filosofia de Eric Voegelin | The Brief |
| 17 | `extra-introdu-o-filosofia-de-louis-lavelle` | extracurricular | Introdução à filosofia de Louis Lavelle | The Brief |
| 18 | `extra-m-rio-ferreira-dos-santos-guia-para-o-estudo-de-su` | extracurricular | Mário Ferreira dos Santos Guia para o estudo de sua obra | The Debate |
| 19 | `extra-pol-tica-e-cultura-no-brasil-hist-ria-e-perspectiv` | extracurricular | Política e Cultura no Brasil história e perspectivas | The Debate |
| 20 | `extra-princ-pios-e-m-todos-da-auto-educa-o` | extracurricular | Princípios e métodos da auto-educação | Deep Dive |

### Lote 31 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `extra-ser-e-poder-princ-pios-e-m-todos-da-ci-ncia-pol-ti` | extracurricular | Ser e Poder Princípios e Métodos da Ciência Política | The Debate |
|  2 | `extra-simbolismo-e-ordem-c-smica-ontem-e-hoje` | extracurricular | Simbolismo e ordem cósmica ontem e hoje | The Debate |
|  3 | `extra-simbolismo-e-ordem-c-smica-ontem-e-hoje` | extracurricular | Simbolismo e ordem cósmica ontem e hoje | The Debate |
|  4 | `extra-sociologia-da-filosofia` | extracurricular | Sociologia da filosofia | Deep Dive |
|  5 | `livro-a-aula-da-vontade` | livro | A aula da Vontade | The Brief |
|  6 | `livro-a-consci-ncia-da-consci-ncia-olavo-de-carvalho` | livro | A consciência da consciência - Olavo de Carvalho | The Brief |
|  7 | `livro-a-consci-ncia-sem-consci-ncia-oiavo-de-carvalho` | livro | A consciência sem consciência - OIavo de Carvalho | The Brief |
|  8 | `livro-a-criminalidade-em-ascens-o-uma-vis-o-civilizacion` | livro | A Criminalidade em Ascensão uma Visão Civilizacional | Deep Dive |
|  9 | `livro-a-deprecia-o-da-humanidade` | livro | A depreciação da humanidade | The Brief |
| 10 | `livro-a-filosofia-de-m-rio-ferreira-dos-santos` | livro | A filosofia de Mário Ferreira dos Santos | The Debate |
| 11 | `livro-a-imortalidade-como-premissa-do-m-todo-filos-fico` | livro | A imortalidade como premissa do método filosófico | The Brief |
| 12 | `livro-a-leitura-hermen-utica` | livro | A leitura Hermenêutica | The Brief |
| 13 | `livro-a-nova-era-e-a-revolu-o-cultural` | livro | A Nova era e a revolução cultural | Deep Dive |
| 14 | `livro-a-organiza-o-econ-mica` | livro | A Organização Econômica | The Brief |
| 15 | `livro-a-tripla-intui-o` | livro | A tripla intuição | Deep Dive |
| 16 | `livro-apresenta-o-do-livro-reflex-es-autobiogr-ficas-de` | livro | Apresentação do livro Reflexões Autobiográficas_ de Eric Voegelin | The Brief |
| 17 | `livro-arte-sacra-estudipez-profana` | livro | Arte sacra_ estudipez profana | The Brief |
| 18 | `livro-as-doze-camadas-da-personalidade` | livro | As doze camadas da personalidade | The Brief |
| 19 | `livro-como-estudar-a-obra-de-olavo-de-carvalho` | livro | Como estudar a obra de Olavo de Carvalho | Deep Dive |
| 20 | `livro-como-tornar-se-um-gostos-o-intelectual` | livro | Como tornar-se um gostosão intelectual | The Brief |

### Lote 32 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `livro-como-tornar-se-um-buscador-da-verdade-introdu-o-ze` | livro | Como tornar_-se um buscador da verdade _Introdução à Zetologia | The Brief |
|  2 | `livro-conselhos-aos-estudantes-de-filosofia` | livro | Conselhos aos Estudantes de Filosofia | The Brief |
|  3 | `livro-considera-es-sobre-o-semin-rio-de-filosofia` | livro | Considerações sobre o Seminário de Filosofia | Deep Dive |
|  4 | `livro-cren-a-e-sistema` | livro | Crença e sistema | The Brief |
|  5 | `livro-debate-entre-alexandre-duguin-e-olavo-de-carvalho` | livro | Debate entre Alexandre Duguin e Olavo de Carvalho | The Critique |
|  6 | `livro-dedu-es-metaf-sicas` | livro | Deduções Metafísicas | The Brief |
|  7 | `livro-dois-m-todos` | livro | Dois métodos | Deep Dive |
|  8 | `livro-duas-vis-es-do-destino` | livro | Duas visões do destino | The Brief |
|  9 | `livro-duvidar-da-d-vida-e-criticar-o-criticismo-prelimin` | livro | Duvidar da Dúvida e Criticar o Criticismo_ PRELIMINARES DE UM RETORNO À METAFÍSI | Deep Dive |
| 10 | `livro-elementos-de-tipologia-espiritual` | livro | Elementos de tipologia espiritual | Deep Dive |
| 11 | `livro-entrevista-com-olavo-de-carvalho-na-revista-rep-bl` | livro | Entrevista com Olavo de Carvalho na revista República | Deep Dive |
| 12 | `livro-esp-rito-e-personalidade-ii` | livro | Espírito e personalidade II | The Brief |
| 13 | `livro-esp-rito-e-personalidade` | livro | Espírito e personalidade | The Brief |
| 14 | `livro-exist-ncia-e-possibilidade` | livro | Existência e possibilidade | The Brief |
| 15 | `livro-experimento-sociol-gico` | livro | Experimento sociológico | The Brief |
| 16 | `livro-experi-ncia-e-presen-a` | livro | Experiência e presença | The Brief |
| 17 | `livro-fugindo-da-filosofia` | livro | Fugindo da filosofia | The Brief |
| 18 | `livro-full-man-responsibility` | livro | Full man responsibility | The Brief |
| 19 | `livro-humildade-rid-culo-e-ironia` | livro | Humildade_ Ridículo e Ironia | The Brief |
| 20 | `livro-implica-es-para-o-brasil-nos-campos-pol-tico-e-eco` | livro | Implicações para o Brasil_ nos campos político e econômico_ em decorrência do at | The Debate |

### Lote 33 (20 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `livro-influ-ncias-intelectuais-que-recebi-at-a-d-cada-de` | livro | Influências intelectuais que recebi até a década de 90 | The Brief |
|  2 | `livro-intelig-ncia-verdade-e-certeza` | livro | Inteligência_ verdade e certeza | Deep Dive |
|  3 | `livro-introdu-o-vida-intelectual-01` | livro | Introdução à vida intelectual 01 | The Brief |
|  4 | `livro-introdu-o-vida-intelectual-02` | livro | Introdução à vida intelectual 02 | The Brief |
|  5 | `livro-introdu-o-vida-intelectual-03` | livro | Introdução à vida intelectual 03 | The Brief |
|  6 | `livro-introdu-o-vida-intelectual-04` | livro | Introdução à vida intelectual 04 | The Brief |
|  7 | `livro-introdu-o-vida-intelectual-05` | livro | Introdução à vida intelectual 05 | The Brief |
|  8 | `livro-introdu-o-vida-intelectual-06` | livro | Introdução à vida intelectual 06 | The Brief |
|  9 | `livro-jean-brun-filosofia-e-cristianismo` | livro | Jean Brun - Filosofia e Cristianismo | The Brief |
| 10 | `livro-mais-musicas-redneck` | livro | Mais Musicas Redneck | The Brief |
| 11 | `livro-medita-o-e-consci-ncia-olavo-de-carvalho` | livro | Meditação e consciência - Olavo de Carvalho | The Brief |
| 12 | `livro-melodias-para-guardar` | livro | Melodias para guardar | The Brief |
| 13 | `livro-musicas-favoritas` | livro | Musicas Favoritas | The Brief |
| 14 | `livro-musicas-redneck` | livro | Musicas Redneck | The Brief |
| 15 | `livro-nota-sobre-richard-dawkins` | livro | Nota sobre Richard Dawkins | The Brief |
| 16 | `livro-nova-lista-de-melodias` | livro | Nova lista de melodias | The Brief |
| 17 | `livro-novas-melodias-para-guardar-na-memoria` | livro | Novas melodias para guardar na memoria | The Brief |
| 18 | `livro-o-criminoso-mentecapto` | livro | O criminoso mentecapto | Deep Dive |
| 19 | `livro-o-falso-div-rcio-de-ci-ncia-e-filosofia` | livro | O falso divórcio de ciência e filosofia | The Critique |
| 20 | `livro-o-mundo-exterior-e-as-perguntas-c-pticas` | livro | O mundo exterior e as perguntas cépticas | The Brief |

### Lote 34 (18 itens)

| # | ID | Tipo | Título | Formato |
|---:|---|---|---|---|
|  1 | `livro-o-que-psique` | livro | O que é psique | The Brief |
|  2 | `livro-o-que-um-milagre` | livro | O que é um milagre | Deep Dive |
|  3 | `livro-o-trauma-da-emerg-ncia-da-raz-o` | livro | O trauma da emergência da razão | Deep Dive |
|  4 | `livro-problemas-de-m-todo-nas-ci-ncias-humanas` | livro | Problemas de método nas ciências humanas | Deep Dive |
|  5 | `livro-quem-gurdjieff` | livro | Quem é Gurdjieff | Deep Dive |
|  6 | `livro-quem-o-sujeito-da-hist-ria` | livro | Quem é o sujeito da História | The Brief |
|  7 | `livro-quest-es-de-simbolismo-geom-trico` | livro | Questões de Simbolismo Geométrico | The Brief |
|  8 | `livro-sistema-filos-fico-olavo-de-carvalho` | livro | Sistema Filosófico Olavo de Carvalho | Deep Dive |
|  9 | `livro-sobre-a-arte-de-estudar` | livro | Sobre a Arte de Estudar | The Debate |
| 10 | `livro-teses-sobre-o-poder` | livro | Teses sobre o Poder | The Brief |
| 11 | `livro-um-guia-para-o-cof` | livro | Um guia para o COF | Deep Dive |
| 12 | `livro-uma-defesa-cr-tica-de-olavo-contra-cantor` | livro | Uma defesa à crítica de Olavo contra Cantor | The Brief |
| 13 | `livro-uma-hist-ria-da-filosofia-para-fil-sofos` | livro | Uma história da filosofia para filósofos | The Brief |
| 14 | `livro-uma-nota-inconclusiva` | livro | Uma nota inconclusiva | The Brief |
| 15 | `tematica-2016` | tematica | Aulas Olavo - COF - 2016 | The Debate |
| 16 | `tematica-apostilas` | tematica | Aulas Olavo - COF - Apostilas | The Debate |
| 17 | `tematica-artigos` | tematica | Aulas Olavo - COF - Artigos | The Critique |
| 18 | `tematica-teoria-estado` | tematica | Aulas Olavo - COF - Teoria do estado | The Debate |
