# Sending 500k requests asynchronously ─ 2022 Zevent Place
Durinmg the 2022 Zevent, a nice addition to previous editions was the [Zevent Place](https://place.zevent.fr/), largely inspired by [/r/place](https://www.reddit.com/r/place/). Supporters could donate by changing the colour of pixels, **but also** by increasing their level, making them more expensive to modify.

### Final Zevent Place canvas
The final 700x700 canvas is as follows.

![final_canvas](https://user-images.githubusercontent.com/114467748/192801571-8415fc8b-0c04-45e8-9392-5ceaa85ac769.png)

### Where to fight your battles
I was curious to see which areas were defended the most during the event. I wrote this piece of code to find it out. It is only meant for personnal use, but feel free to play around with it. Though one should be **aware of potential security issues** while using one's authorization key (Zevent Place requires users to be logged in to access the pixels' level data).

Since there are about 500k pixels, it was unthinkable to loop through them by sending a request, waiting for the server to respond, and then carry on. This was thus a good opportunity to use the `aiohttp` module and asynchronous requests. The final result looks like this:

![final_levels](https://user-images.githubusercontent.com/114467748/192801911-88f29ee4-cdac-43d3-a3fc-c38896352ccc.png)

As one could have guessed, the pixel on the top left was by far the most sought after! The final bid/donation on it was for 122.3€!! But other than that, it is fun to see that lots of designs were built on solid grounds, not only by repainting over and over again!

To conclude, I think that the organizers will soon release the whole dataset, hence there will soon be absolutely no use to this code :)

Cheers
