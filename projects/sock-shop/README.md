# Sock Shop multi-repository demo

This project indexes the public Sock Shop services as independent Git repositories.
It is deliberately a non-trivial demo: the Node front-end calls several backend
services, and the order path crosses payment, shipping, and user services.

The sources are not committed. Fetch them with:

```bash
scripts/fetch-sock-shop.sh
cp projects/sock-shop/.local.yaml.example projects/sock-shop/.local.yaml
python3 scripts/graph.py validate sock-shop
python3 scripts/graph.py index sock-shop
python3 scripts/graph.py generate sock-shop
```

The source repositories are from the public `microservices-demo` GitHub
organization. Review each upstream repository's license and notices before
redistributing its source. This toolkit only stores graph metadata and clone
instructions.
