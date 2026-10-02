# Map data

`src/js/art/mapdata.js` is generated from Natural Earth data (npm package `world-atlas`, 50 m countries)
with `d3-geo` (conic conformal projection centred on 15°E). Re-generate with:

```bash
cd tools/mapbuild && npm init -y && npm i world-atlas@2 d3-geo@3 topojson-client@3
node build.mjs && cp mapdata.js ../../src/js/art/mapdata.js
```

Field positions are approximate (decorative); only the four featured fields are labelled.
