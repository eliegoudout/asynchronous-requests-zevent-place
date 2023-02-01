# Sending 500k requests asynchronously ─ 2022 Zevent Place
During the 2022 Zevent, a nice addition to previous editions was the [Zevent Place](https://place.zevent.fr/), largely inspired by [/r/place](https://www.reddit.com/r/place/). Supporters could donate by changing the colour of pixels, **but also** by increasing their level, making them more expensive to modify.

### Final Zevent Place canvas
The final 700x700 canvas is as follows.

![final_canvas](https://user-images.githubusercontent.com/114467748/192801571-8415fc8b-0c04-45e8-9392-5ceaa85ac769.png)

### Where to fight your battles
I was curious to see which areas were defended the most during the event. I wrote this piece of code to find it out. It is only meant for personnal use, but feel free to play around with it. Though one should be **aware of potential security issues** while using one's authorization key (Zevent Place requires users to be logged in to access the pixels' level data).

#### Sequential or asynchronous?
Since there are about 500k pixels, it was unthinkable to loop through them by sending a request, waiting for the server to respond, and then carry on. This was thus a good opportunity to use the `aiohttp` module and asynchronous requests. The final result looks like this:

![final_levels](https://user-images.githubusercontent.com/114467748/192817824-ec49a779-01fe-4c4a-9697-e1a3a4fce204.png)

As one could have guessed, the pixel on the top left was by far the most sought after! The final bid/donation on it was for 122.3€!! But other than that, it is fun to see that some of the designs were built on solid grounds, not only by repainting over and over again! Small and consensual logos didn't need much leveling up, while bigger, and maybe more dividing ones benefited from numerous pixel upgrades.

### Loading data
You can read the resulting data from `human_readable_levels.dat` and load it from `final_levels.npy` with
```python
import numpy as np
data = np.load('final_levels.npy')
```
```
>>> data
array([[1223,  130,   20, ...,    4,   13,  136],
       [ 137,  101,   36, ...,    3,    2,   17],
       [  28,   23,   19, ...,    1,    3,    9],
       ...,
       [  20,    3,    3, ...,    7,    4,   11],
       [  25,    5,   20, ...,    5,    5,   13],
       [ 157,   28,   21, ...,    4,    9,  184]])
```

### Conclusion
To finish it off, I should mention that the organizers will soon release the whole dataset, hence there will soon be absolutely no use to this code :)

Cheers!
