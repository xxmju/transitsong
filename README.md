# transitsong
Sonification of TESS transits between 200-900 Hz. 

## How to install:
```pip install transitsong```

### Dependencies:
- numpy
- sounddevice
- lightkurve
- matplotlib
- scipy
- moviepy

## How to use:
```import transitsong```
```from transitsong.main import Transit```
```transit = Transit(tic_id, sector, window)```
- tic_id: str
- sector: int
- window: list of length 2, start and end of desired section