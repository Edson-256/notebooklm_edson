# Testes

Só biblioteca padrão (`unittest`) — sem pytest, sem rede, sem `nlm` real.
O CLI `nlm` é simulado por `tests/_helpers.py::FakeNlm` (executável falso no PATH).
Todos os dados são fictícios.

```bash
python3 -m unittest discover -s tests -t . -v
```
