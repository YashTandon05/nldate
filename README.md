# nldate

A small Python package for parsing simple natural-language dates.

## Example

```python
from datetime import date
from nldate import parse

parse("5 days before December 1st, 2025")
parse("next Tuesday", today=date(2025, 12, 1))
