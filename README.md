# Tap-Zepto

## Usage

```bash
tap-zepto --config config.json --discover > catalog.json
singer-discover --input catalog.json --output catalog-selected.json
tap-zepto --config config.json --catalog catalog-selected.json > data.txt
```
