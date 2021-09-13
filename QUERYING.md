# Common Query Language (CQL) Operators

`stac-fastapi` conforms to OGC API Feature - Part 3: Filtering and the Common Query Language (CQL). <br>
Support is in beta as of v2.1.0, released August 26 2021 (ref.: https://github.com/stac-utils/stac-fastapi/releases/tag/2.1.0). <br>

Here are the common CQL operators used for querying STAC API. <br>
See https://portal.ogc.org/files/96288 for the specs. <br>

See `stac_api.postman_collection.json` for sample queries.

## Logical Operators

Operators : AND, OR, NOT


## Comparison Operators

Operators : EQ, LT, LTEQ, GT, GTEQ, LIKE, ISNULL, BETWEEN, IN


## Spatial Operators

Operators : EQUALS, DISJOINT, TOUCHES, WITHIN, OVERLAPS, CROSSES, INTERSECTS, CONTAINS <br>
See https://portal.ogc.org/files/96288#enhanced-spatial-operators


## Temporal Operators

Operators : AFTER, BEFORE, BEGINS, BEGUNBY, TCONTAINS, DURING, ENDEDBY, ENDS, TEQUALS, MEETS, METBY, TOVERLAPS, OVERLAPPEDBY <br>
See https://portal.ogc.org/files/96288#enhanced-temporal-operators
