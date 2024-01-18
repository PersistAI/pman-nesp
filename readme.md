## intro
This is a flask app that uses florian-lapp's [NESP-Lib](https://github.com/florian-lapp/nesp-lib-py) to communicate with the NE-1000 Syringe Pumps. Two PMAN endpoints are provided: `/pman/pull` and `/pman/push`. The argument format is shown below: 

```
[volume, pump_rate]

volume: mL
pump_rate: mL/min
```

When the pump finishes running, the endpoints return their response.
