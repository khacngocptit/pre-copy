# Menu Adjuster for Preschoolers

## Table of Contents

- [Getting Started](#getting_started)
- [Usage](#usage)

## Getting Started <a name = "getting_started"></a>

### Prerequisites

```
python 3
```

### Installing

```
pip3 install -r requirements.txt

```

## Usage <a name = "usage"></a>

```
python3 main.py sample/[menu.json]
```

or

```python
from main import Adjuster
[...]
adjuster = Adjuster(input)
menu, report = adjuster.run()
[...]
```
```
run: uvicorn api:app --reload
```
## Backup -> tạo ra i2
Login gitlab
```
docker login registry.gitlab.com
```
Gán tác cho docker để push
```
docker tag preschooler-menu registry.gitlab.com/ndhpro/preschooler-menu

```
push image to gitlab
```
docker push registry.gitlab.com/ndhpro/preschooler-menu

```
## Run i3
ở folder preschooler-menu chạy để được i3
```
docker-compose up -d
```# pre-copy
