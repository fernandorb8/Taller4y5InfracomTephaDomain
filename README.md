# Taller 4 y 5 Infraestructura de comunicaciones

Tepha

Pegroo Fabián

Ferchito

For creating 250Mb and 500Mb files:

```
dd bs=1024 count=512000 </dev/urandom >myfile_500.txt
```

```
dd bs=1024 count=256000 </dev/urandom >myfile_250.txt
```