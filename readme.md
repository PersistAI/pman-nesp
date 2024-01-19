## intro
This is a flask app that proides a communication intereface for the NE-1000 Syringe Pumps. Two PMAN endpoints are provided: `/pman/pull` and `/pman/push`. The argument format is shown below: 

```
[address, volume, pump_rate]

volume: mL
pump_rate: mL/min
```
