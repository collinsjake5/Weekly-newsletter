---
title: Ashok Elluswamy: Building Foundational Models for Robotics at Tesla
url: https://www.youtube.com/watch?v=LFh9GAzHg1c&list=WL&index=9&t=1s
channel: Matroid
type: robotics
highlights: Foundational models for robotics
---

[
Search in video
0:00
Hey everyone, my name is Ashok um
0:02
Eliswami. I work at Tesla. I've been
0:03
there for the last 12 years and I lead
0:05
the Tesla AI team. Um thanks for having
0:08
me today. Uh would like to present about
0:10
the things that the team has been
0:11
working on and like you know what is the
0:13
uh you know the mission of the team and
0:15
what is the upcoming road map of uh you
0:18
know the team's work
0:20
to start out Tesla's mission is
0:22
producing amazing abundance for the
0:24
entire world. Um we you know Tesla has
0:28
been historically known for producing
0:30
vehicles. Uh but then the more uh
0:32
important thing is that these vehicles
0:34
can drive themselves. They have all all
0:36
the vehicles have uh all the necessary
0:38
sensors and compute to do autonomous
0:40
driving. Here you can see our um robot
0:43
taxi service operating in Austin. Uh
0:45
there's no one inside the car that's
0:47
driving the car. This is just a
0:48
passenger hailing a ride and then the
0:50
car just uh drives them around all of
0:52
Austin. This is publicly available. um
0:55
as of like earlier this month. Um,
0:57
previously we used to have safety
0:59
monitors to just like you know supervise
1:01
FSD but now that's gone and then people
1:04
can just you know get in the car you
1:05
know they already have the address
1:07
punched in so they can hit start trip
1:08
and then the car just takes them uh
1:10
wherever they want and these are public
1:11
roads uh with like you know dense
1:13
traffic and everything and this is all
1:16
driven by uh cameras and AI
1:20
and the future of the company is not
1:21
just like vehicles we also have like all
1:24
working on like humanoid robots uh that
1:26
sort of like go to the next level of
1:28
functionality. Um like the Tesla
1:31
vehicles are like low cost scalable
1:32
solution to transport and humanoid
1:34
robots are a lowc cost scalable solution
1:36
to automate like all physical work. The
1:40
reason for humanoid robots is that they
1:42
you know they're backwards compatible.
1:43
You can like you know send humanoid
1:45
robots to any mission and just like how
1:47
humans can go in and then uh you know
1:49
solve problems in the real world. Um it
1:51
uses the same interface. Uh so it's
1:53
backwards compatible. So you don't need
1:55
to build any new infrastructure to
1:57
welcome these robots into our world.
1:59
They are already ready to go and make a
2:01
big impact.
2:05
In addition to having the robot access
2:06
service, we also have deployed uh full
2:08
self-driving to all the uh Tesla owners
2:11
who are who has purchased this. And
2:13
these are video clips of uh you know um
2:16
people who have engaged FSD getting
2:18
saved by uh the software itself you know
2:21
from sort of tricky situations um
2:25
and here for example there's a bus
2:26
coming and the vehicle automatically
2:28
reverses to make way for them just like
2:30
shows a lot of intelligent behavior and
2:32
this is uh in every Tesla uh with uh
2:34
hardware three and four
2:38
and this is al the safety improvements
2:40
also quantitatively show Here we are
2:43
showing the uh miles before a collision
2:46
happens in the entire vehicle fleet. Uh
2:48
and the uh blue chart that's much higher
2:50
than the rest is actually when you use
2:53
uh full self-driving to drive those
2:54
miles. And then if you just use the you
2:57
know um traditional driving with active
3:00
safety, you can get some safety
3:01
improvements compared to not having any
3:02
active safety. It's very clear that
3:05
using self-driving to drive you around
3:06
as opposed to manually driving the car
3:09
definitely makes you safer over billions
3:11
of miles of study. And this is not just
3:14
on the highway or something like that.
3:15
Even highway off highway in both cases
3:18
uh it is at least 2x better than uh the
3:21
baseline of driving manually. So you
3:23
know if you have a Tesla you should
3:24
definitely uh use self-driving. Uh I
3:27
personally use it all the time.
3:30
So today we are going to cover you know
3:32
like what makes a software work u sort
3:35
of what are the challenges in building
3:36
such a system uh and like you know how
3:38
do we evaluate the safety of this
3:42
first of all um Tesla uses an end toend
3:45
driving system to u create the
3:47
self-driving software uh you might think
3:49
that in the modern era obviously you
3:50
should have like you know end to end
3:52
systems but this is uh not uh
3:54
contemporarily agreed upon you know for
3:56
example many competitive solutions use
3:59
uh sort of model approaches that have
4:01
separate like perception stacks,
4:03
planning, prediction stacks and so on.
4:05
Uh and Tesla has foregone all of those
4:07
systems to have a single end to end
4:09
neural network that takes in raw sensor
4:11
inputs. Uh which is predominantly just
4:14
camera videos from the eight cameras in
4:16
in the car but also things like you know
4:18
the navigation instructions uh kinematic
4:20
states like the vehicle speed, steering
4:22
etc. uh audio uh to just come up with
4:26
how the car should behave uh and like
4:28
what is the next action in terms of you
4:29
know steering uh or like uh jerk or
4:33
something like that. uh and the reason
4:34
for this is that u I guess I can go over
4:38
uh some of the reasons first of all like
4:40
codifying uh everything in like you know
4:42
rules based or like doesn't have to be
4:44
even rules based but having like modular
4:46
systems they have like very um leaky
4:49
abstractions um it's it's going to be
4:52
hard to spe communicate every single
4:54
detail the uncertainty that the raw
4:56
measurements can have to the lower level
4:57
systems uh and all of these are like
4:59
tightly coupled like you uh you can't
5:01
like clearly separate the concerns s
5:04
that traditionally we have been taught
5:05
in like you know in good software
5:07
engineing practices you want to like
5:08
separate the concerns make it modeler
5:10
but that's just very hard to do in real
5:12
world robotics you want the information
5:14
to flow densely uh a few examples here
5:18
uh you know typically going into the
5:20
oncoming lane is like quite bad like you
5:23
would not want to go into the oncoming
5:24
site there could be oncoming vehicles at
5:26
high speed you don't want to go in there
5:28
but then there is a water puddle here so
5:30
you know in in case you also have you
5:32
can you can add a separate rule that
5:33
says okay avoid puddles but then now you
5:35
have to solve this tiny trolley problem
5:37
of should I go over this puddle or
5:39
should I go into the oncoming side and
5:41
it depends on not just these two
5:43
conditions it also depends on uh whether
5:45
there's oncoming car or not but just
5:47
because the oncoming car is not there
5:48
doesn't mean you can go there because
5:50
you know you might not have the
5:51
visibility for various different reasons
5:54
um so you got to like holistically
5:56
consider the entire scene to come up
5:57
with the decisions you can't just decide
6:00
based on independent rules or
6:01
independent like logical elements here.
6:06
Like here's one more example. Here's
6:08
some, you know, this chicken that wants
6:09
to cross the road on the left side here.
6:11
Um the car actually on FSD patiently
6:14
waits for the chickens to cross on the
6:15
left side. And if you're paying
6:17
attention, there's like one last
6:19
chicken. There's a stagler chicken
6:20
there. Uh it still like waits for it.
6:25
Yeah.
6:27
Waits for all the chicken to cross and
6:28
then autonomously proceeds.
6:30
Why are they crossing?
6:31
Yeah. they want to test FSD.
6:35
And on the right side, um there's a
6:37
similar scenario. There's a bunch of
6:38
geese on the road. Um and the there's no
6:41
one inside the car here. This is using
6:42
the smart summon software. Uh then the
6:45
geese, they're not crossing. They're
6:46
just like, you know, they're just like
6:48
standing there and the car just backs up
6:50
and then goes around them. So you have
6:52
to like see this like subtle cues of how
6:54
these like you know legs of these birds
6:56
are moving to know that they're either
6:58
intending to cross or not intending to
7:00
cross and do the appropriate action.
7:02
Like if you had explicit perception
7:04
prediction and so on what are we going
7:05
to do like have a chicken leg detector
7:07
and then like predict how the chicken's
7:09
going to move and then uh take action. I
7:12
just think it's too complicated in an
7:13
end to end system. All of this
7:14
information can flow from the pixels
7:16
directly to control. Um
7:20
it also you know overall uh is has
7:23
determin deterministic latency like for
7:26
driving you have to produce actions in
7:27
the real time. You you can't take um
7:30
very long time to process regardless of
7:32
how long we think the world is changing
7:34
around the car. So the latency is quite
7:37
important and with neural networks it's
7:38
way easier to control the latency. You
7:40
get a lot of determinism um to take
7:43
actions. It's very easy to validate in
7:45
that kind of the system sense. Uh and
7:47
overall it's on the right side of the
7:48
bitter lesson. You know, we're betting
7:50
on uh scaling with like the new network
7:52
size, data, uh more training compute,
7:55
more rewards and so on as opposed to uh
7:57
handgineered processes.
8:01
So then okay, it sounds so great then
8:02
why why don't why doesn't everyone adopt
8:04
this? Like why isn't this just common
8:06
place? Why is you know Tesla or a couple
8:08
of other companies uniquely doing this
8:10
uh compared to the rest of the
8:11
autonomous driving industry?
8:13
First I would say is the curse of
8:14
dimensionality. U you know in order to
8:17
make the the car itself has uh eight
8:20
cameras and they are like high
8:21
resolution cameras. You know this 5
8:22
megapixels and they run at pretty high
8:24
frame rate and then you need a
8:26
reasonable size history to make
8:27
decisions. You know if you come to a
8:29
stop sign you need to like remember who
8:30
came first to the stop sign you know who
8:32
needs to go and so on. So you need a lot
8:34
of context to solve these uh
8:36
self-driving problem and pretty much um
8:38
any robotics problem. I would say even
8:40
this history is not like necessarily
8:41
sufficient. You might in theory want
8:43
infinite history to solve robotics in
8:45
general, but say we can get away with a
8:48
30-cond history. Uh, and even then if
8:51
you just just compute the raw amount of
8:53
bytes that's streaming into the network,
8:55
it's roughly, you know, it depends on
8:57
how you tokenize it, you can think of it
8:59
as two billion tokens coming into the
9:03
network. And then in the end you had to
9:04
produce like two actions you know
9:05
roughly what is the steering angle for
9:07
the next time step and what is the uh
9:09
acceleration on brake uh for the next
9:11
time step right like so you're
9:13
compressing down this ridiculous amount
9:15
of in uh information like two billion
9:17
tokens input and it produced two actions
9:20
this be a trivial job if you just
9:21
randomly took two bytes and then like
9:23
piped it out right but you had to take
9:24
the two correct actions and so you have
9:26
to causally understand what amongst this
9:29
giant stream of bytes and bits uh is um
9:32
uh is The reason why I should take these
9:34
two correct actions that you know for
9:36
example the human took or like whatever
9:37
optimize the reward like learning that
9:39
correct causal mapping is very difficult
9:41
because the network can learn all kinds
9:42
of speurious correlations you know I
9:44
should break here because the tree
9:45
branch was moving certain way like you
9:47
don't want to learn speurious
9:48
correlations you want to learn the
9:49
correct correlation that I'm breaking
9:51
right now because the vehicle in front
9:52
of me has the know turn signal on or
9:55
something like that
9:57
um luckily the Tesla fleet is quite
10:00
large uh and you can collect a
10:01
significant amount of data from the
10:03
Tesla fleet um to rough order of
10:06
magnitude like the entire fleet can
10:08
produce 500 years of driving data on
10:11
every single day. But obviously most
10:13
data is like boring like you know most
10:14
people are just driving on the highway
10:15
minding their own business. It's not
10:17
interesting. So and it'd be a tremendous
10:19
waste of resources to literally collect
10:21
all this data and then filter
10:23
afterwards. So what we do is instead
10:25
just identify what is interesting data.
10:27
There's a lot of work that goes into
10:29
identifying what is interesting. But
10:30
once you identify the interesting data,
10:32
then you know, okay, now there's a
10:34
school bus here and that's more
10:35
interesting or there's a fire engine
10:36
crossing and that's more interesting and
10:37
so on. Uh and you can like sort of
10:40
source this uniquely interesting data uh
10:42
from this ocean of uh mundane data. Then
10:46
having a large fleet allows you to very
10:48
quickly collect interesting data that's
10:50
very rare for other people to collect.
10:52
Here's an example of what that could
10:54
look like. you know, um like watch for
10:56
yourself, but then you know, cars.
10:58
Um yeah, just like
11:13
Yeah, just like really hard to collect
11:14
this data otherwise you can't stage
11:16
these kind of things because you know
11:17
there's a lot of actors involved, a ton
11:19
of traffic, they can be hazardous.
11:31
Yeah. And these kind of issues like you
11:33
they're happening every day but very
11:34
rarely right but you across the entire
11:36
fleet you can definitely collect a lot
11:38
of them
11:40
and if you collect a lot of this data
11:41
and then train a system then you can get
11:43
extremely good proactive safety and also
11:45
like generalization to rare events.
11:47
Here's an example where self-driving
11:49
software is driving here and this person
11:51
in front of us sort of um skids out uh
11:59
the barrier here but the self-driving
12:01
software realized this quite early and
12:02
then break automatically uh and then
12:05
like avoided this you know what could
12:07
have been one more collision here and
12:10
what I like to emphasize here is like
12:11
how early it reacts to this stuff and
12:13
you can see like sort of this like
12:14
velocity here of the vehicle um it
12:19
starts breaking
12:21
already at this time step uh as as seen
12:25
by uh this like planned velocity.
12:29
The the the lead vehicle in front of us
12:31
hasn't even crashed here. It's just like
12:33
it could have been doing a lane change.
12:34
It's just going from this lane to this
12:35
lane but it already realizes that
12:37
something is wrong here. Something is
12:39
out of uh something is oddier. So it
12:42
already starts applying pretty
12:43
significant amount of break. what you
12:45
know people might uh be a little bit
12:47
shook because it anticipates something
12:49
bad is going to happen many seconds in
12:52
advance of the actual event happening.
12:54
Um so you you need the predictive
12:56
intelligence of okay this the y rate of
12:59
this other vehicle is more so than
13:01
necessary for a lane change maybe
13:02
they're going to crash what if they
13:04
crash and come into our path hence we
13:06
must break right now and this kind of
13:08
like third order intelligence needs to
13:10
be done uh in real time uh while
13:12
processing you know like there could be
13:14
like this these vehicles could be coming
13:15
here there's like so many other bites
13:16
here right like it needs to focus on the
13:18
correct things to make this conclusion
13:20
to hit the brakes in a confident manner
13:23
uh and And that that's what all this
13:24
data is required for not for like you
13:25
know driving around the block here.
13:30
So it's end to end system you know like
13:31
does it mean that you can't understand
13:33
what it's doing? Um how do you debug if
13:36
there's a failure? Um even though it's
13:38
an end toend system there's all kinds of
13:41
probes you can attach to the system. Uh
13:42
and you can like study whether it fully
13:45
understands the world around it. For
13:47
example, uh in addition to just getting
13:49
the next action, you can it's just like
13:51
reasoning where you can, you know, look
13:52
at the reasoning traces and then know
13:54
whether the reasoning was consistent or
13:56
like the reasoning was correct with
13:57
respect to the action it took. Um and
14:00
reasoning here might need not be just
14:02
text based reasoning as you know
14:03
traditional LLMs do. The the reasoning
14:05
here can use uh sort of like geometric
14:07
reasoning you know like where are these
14:08
vehicles, where are the other obstacles,
14:10
how are they going to move forward. But
14:12
not all reasoning needs to be produced
14:13
at test time. But you at training time
14:15
you can have all this reasoning attached
14:17
to it and then at test time you can
14:18
detach it uh and then only use it for
14:20
either debugging or like the reasoning
14:22
can be implicit. You don't have to
14:23
explicitly manifest the reasoning.
14:26
Uh one form of such reasoning is like 3D
14:28
reasoning like I mentioned. Um so here
14:31
um for example we can use um uh gosh
14:35
platting as a representation for u the
14:38
3D world around the vehicle. Um one one
14:41
thing we do well is that for example
14:42
traditional gshian splatting which is
14:44
used to reconstruct 3D worlds um is it
14:48
usually looks very good when you're
14:49
close to the training views of the
14:51
gshian splatting but when you are off
14:53
the manifold of the training views and
14:55
you if if you deviate and then you go to
14:56
novel views that are far away the
14:58
generalization sort of like fails very
15:00
poorly. So if you took a video clip from
15:02
the vehicle and you run traditional
15:03
gshian splatting, you get the video on
15:05
the left most side and the middle video
15:07
here is Tesla's own uh like generative
15:09
gshian splatting which has very good
15:11
generalization even beyond the uh train
15:14
views and you can see that uh you the
15:17
semantics are um quite correct on like
15:20
which type of vehicle it is and so on.
15:22
Um and all of this happens way faster
15:24
than traditional gshian splatting.
15:26
traditional gshian splatting can take
15:27
like for example 30 minutes uh or or
15:30
even more sometimes versus Tesla's own
15:32
system can run on the order of hundreds
15:34
of milliseconds um doesn't require any
15:36
kind of initialization it's all neural
15:38
network based and this is part of the
15:40
same neural network that produces the
15:42
control action so it understands
15:44
geometry and can produce and explain the
15:46
3D geometry around the vehicle um along
15:49
with the action
15:51
here one more demonstration of this so
15:53
it takes in the videos at the top as the
15:55
the network takes the on the top as an
15:57
input. I can like entirely generate 3D
15:59
world that's interactable. You can like
16:01
move around uh and you can like see what
16:04
the network thinks the world around it
16:06
looks like not just in the camera's
16:08
point of view but in a 3D view. Uh so
16:11
this really makes it understand um this
16:14
basically helps with also learning the
16:16
correct correlations. You know it knows
16:17
that these pixels in the image space or
16:19
video belong to this vehicle and so on.
16:26
In addition to um uh geometric
16:30
reasoning, you can also do just text
16:31
based reasoning. Uh for example, here
16:33
there's some road closure. Uh you can
16:35
reason out in a mix of language and also
16:38
pointing to things on the videos. You
16:40
can say okay the detour sign here I must
16:42
turn left. Uh it like so it has this
16:46
comprehensive understanding of the world
16:47
around it. Um obviously like producing
16:50
all of this at inference time is going
16:52
to be quite challenging because you
16:53
can't produce all these number of these
16:55
many tokens in a very short amount of
16:57
time because the car has to produce
16:58
actions in real time. But a lot of this
17:00
can be implicit. You don't have to
17:01
explicitly manifest it or you can do it
17:03
offline during training time to just
17:04
distill all of this knowledge into the
17:06
neural network.
17:08
The last uh challenge I would say is
17:10
evaluation uh which I personally think
17:13
is the hardest of the three challenges
17:14
because you know self-driving is a
17:16
longtail problem. You want to verify
17:17
that uh even the tail cases work very
17:19
well. Um and this is a closed loop
17:22
system. So developing evaluations for
17:25
closed loop requires a good simulator or
17:28
either testing in the real world. But
17:29
testing in real world for all longtail
17:30
situations is extremely difficult. So
17:33
what we did was we trained a world
17:35
simulator neural network. This uh this
17:38
is trained on data where you have paired
17:41
uh state and action pairs which is very
17:42
easy to collect and then you just uh
17:44
invert it as in given video and action
17:47
it produces the next state which is like
17:50
given current video uh and then current
17:52
you know steering or axle pedal uh
17:54
actions it produces what the next video
17:56
frames is going to look like.
17:59
Then once you have this you can connect
18:00
this to the policy neural network that
18:02
takes the actions. So the uh world
18:05
simulator produces the next video frame
18:07
and then come uh and the other sensor
18:08
measurements. Uh this is consumed by the
18:11
policy neural network that then takes
18:12
the next action and then they just go in
18:14
round robin fashion simulating the world
18:16
and these two neural networks are
18:18
trained uh differently. So they they
18:20
don't actually like the um the world
18:23
neural network can use privileged
18:24
information that the policy does not
18:26
have access to uh and that is how they
18:28
can be verified independently.
18:32
So here's an example of uh video that is
18:34
generated by the neural network. Um
18:38
this the neural network produces the um
18:41
uh eight camera videos uh at 36 fps and
18:45
5 megapixel resolution. Uh this is a
18:47
very long generation. This I think this
18:49
video is like about a minute long. Uh
18:51
but all the pixels here are generated by
18:53
neural network. And you can see how, you
18:55
know, the vehicle's moving around the
18:57
van and everything is consistent across
18:59
different cameras as the other objects
19:01
move around.
19:24
Yeah, as I mentioned, every every
19:26
camera, every pixel here is fully
19:28
generated. There is no real pixels here,
19:29
even though it looks quite realistic.
19:34
The the reason for doing this again is
19:35
for evaluation purposes. So what we want
19:37
to do is we add some historical issue.
19:39
We want to replay them on newer policy
19:41
models to verify that have they solved
19:43
the issue. Uh for example on the left
19:46
side here there was an historical issue
19:48
where the you know the vehicle was
19:49
driving a bit close to the pedestrian
19:51
and then the human driver intervened on
19:53
him and then now we have a newer neural
19:55
network that should have improved this
19:57
and then we try to replay this on the
19:59
same video clip um and then verify that
20:02
now have we improved on the performance
20:04
compared to the original neural network.
20:06
So on the right side you can see the
20:08
same scenario has been reproduced at
20:10
least the important details for example
20:11
the stash pin is missing but that's not
20:13
the important detail here the important
20:15
detail was a pedestrian and then the dog
20:16
that they were walking and that is
20:18
reproduced accurately and then now you
20:20
see that the new policy deviates
20:22
correctly away from the pedestrian.
20:27
You can also inject newer issues that
20:28
were not originally found. So you can
20:30
take any clip here this like driving
20:31
straight and then you can modify the
20:34
video to inject adversarial scenes. You
20:38
can take the same same scenario and then
20:40
just inject different motion. This uh
20:42
lets the um uh simulation system to be
20:46
used in like novel ways and then like
20:48
test corner cases that might not even be
20:50
explored at the fleet scale.
20:56
And if you you know reduce the test time
20:58
compute significantly, you can also just
21:00
make this work in a real-time basis. Um
21:03
here uh you can see that this these are
21:05
all generated pixels. They're driving in
21:07
a fully synthetic world uh using just
21:10
like you know some game engines like
21:13
steering and um pedal control and you
21:15
can just like drive around uh sort of in
21:17
real time and all the pixels here are
21:19
generated. Obviously, it's running at
21:20
real time, so it requires some reduced
21:22
test time compute. Um, but then you it's
21:25
still pretty reasonable for uh driving
21:28
in real time.
21:48
And all of this doesn't uh just uh is
21:51
needed for uh self-driving like the the
21:53
end to-end driving neural network is not
21:55
just driving neural network. It's
21:56
actually a foundational neural network
21:58
for robotics. The same for the
22:00
simulation neural network too. Both of
22:01
them are trained on common data across
22:04
all of the robots. Um here you can see
22:06
that the same video generation network
22:09
also generalizes to uh generating indoor
22:12
scenes for optimus to walk around.
22:15
These are also like controllable. Uh
22:17
here you can take a single u video clip
22:20
and then convert it to be an action
22:22
based one and you can take the action to
22:24
go straight or turn left or turn right
22:26
and then you can see that the uh video
22:28
generation properly reflects the
22:30
actions. So it water I explained earlier
22:34
today is not just for uh the vehicle but
22:37
also for human robots or in fact any
22:39
robots for that matter.
22:42
Um you also see it work for uh
22:44
manipulation. It can you know is this
22:46
again action condition where it can uh
22:48
open a drawer and then you can see that
22:50
the video um sort of like reflects
22:52
opening a drawer uh or like picking up
22:55
an object or something like that.
23:02
Okay, the benefit of using uh generative
23:05
like world models or like uh neural
23:07
network based world models is that yeah
23:08
it can basically like you know
23:10
everything is green everything is great
23:12
you should definitely do it just you
23:13
know you have to spend a lot of money
23:14
but otherwise it's great
23:18
um so yeah what is the team working on
23:20
again like I said bringing in amazing
23:22
abundance to this world in the form of
23:25
widespread self-driving cars we going to
23:27
have uh Cyber caps. The vehicles that
23:29
you see here, they are designed for
23:31
autonomy. They don't um have any
23:33
steering wheel or axle pedal or brake
23:35
pedals. Is meant for full self-driving.
23:38
Um only um it's coming later this year.
23:41
Um this will have the lowest cost of uh
23:44
transportation even beating public
23:45
transport uh while delivering a premium
23:49
point-to-point transportation experience
23:51
for everyone. Um we'll also have Optimus
23:54
robots in production. Uh and together
23:57
they should significantly
23:59
u reduce the cost of doing things in the
24:01
real world. Um thus improving
24:03
productivity and value for the entire
24:05
world. And if you're interested in
24:06
working on such problems, please come
24:08
join the team. There's a lot of uh
24:10
interesting problems still. It's u while
24:12
it works quite well, there's still a lot
24:14
of other challenges that are technically
24:15
interesting and challenging and very
24:17
meaningful to this world. Uh and with
24:19
that, thank you everyone.
24:23
[applause]
24:30
We have time for a couple of questions.
24:34
Yeah. Go ahead.
24:35
Why are you so convinced that you can
24:37
solve this self-driving
24:39
uh challenge only with cameras? I mean,
24:41
you seem quite convinced.
24:43
Yeah. It's like, how did you get here
24:45
today?
24:47
With a
24:48
with a Okay. All right. [laughter] But
24:50
many people drove here with their own
24:51
eyes. Um,
24:54
and then, you know, obviously you can
24:55
like walk around this building with your
24:57
own eyes. Like it's it's so obvious that
24:59
you can solve this with cameras. For me
25:01
at least. Um, like why wouldn't you
25:03
solve with cameras? It's like 2026.
25:06
Like it's uh it should be solved with
25:08
cameras just like how every other human
25:10
and animal lives around this world. It's
25:12
just like you know very simple sensors.
25:14
The self-driving problem is you know
25:16
thought of as a sensor problem. It's
25:18
actually not a sensor problem. It's an
25:19
AI problem like you need to understand
25:20
the world. You need to understand what
25:22
other people are going to do. Uh and the
25:24
cameras have enough information um
25:27
already. It's just the problem of
25:28
extracting the information which is an
25:30
AI problem. Um the the sensor solution
25:33
was developed back in 2008 or whatever
25:34
during DARPA DARPA days when there
25:37
wasn't enough intelligence around back
25:39
then to extract this information. It was
25:42
and that's why you um need to depend on
25:45
all these other sensors back in the day.
25:47
But nowadays intelligence has grown
25:48
tremendously. You can obviously extract
25:51
this information. Uh and uh once you
25:53
have the AI, you don't need the other
25:55
sensors. You just you need the
25:58
information which is the cameras do
25:59
provide.
26:02
Go ahead.
26:05
Yeah. Thank you for the presentation.
26:06
With your fully generative world
26:08
simulator, are you also providing
26:10
rewards or penalties if collisions occur
26:12
or other?
26:13
Yeah. Cool. Yeah, we do. And does the
26:14
model itself output those penalties or
26:17
Yeah, we can have a model or we can
26:18
also, you know, have explicit uh
26:20
collision checks.
26:24
Are you adding anything else to the real
26:26
world like you know every intersection
26:27
you could have extra mirrors or
26:29
something that really adds to
26:31
not you can't see across the corner,
26:33
right? So
26:34
I I I think those would be like cherry
26:36
on the cake. um humans are able to
26:39
navigate the real world without with
26:41
this we want to navigate the real world
26:42
with the same infrastructure and tools
26:44
that humans have. Uh not to say that we
26:46
can't do better than them but then uh we
26:49
shouldn't use those other things as a
26:51
crutch to make the solution work. We
26:53
should solve the problem. We we solve
26:54
the core problem and then you can add
26:56
other infrastructure to make it even
26:57
better. Uh and for and the team is just
26:59
focused on solving the core problem
27:01
right now.
27:06
You had a slide that said large model
27:08
running on 36 hertz. Can you please
27:10
elaborate on that 36 Hz part?
27:14
Uh that is the frequency at which we
27:16
issue the control commands uh to the
27:18
car. Uh it's meaning to say that you
27:20
issue a control command once every 36
27:23
times a second like roughly 20 every 27
27:25
milliseconds you send what the car
27:28
should be doing. Yeah.
27:32
Uh can you talk about the human voice?
27:35
How do Tesla robots car uh interfate
27:41
with people? Do you have a voice? Can
27:43
you speak?
27:44
Uh if somebody want to talk to Tesla
27:46
car, can you respond? Thank you.
27:49
Yeah, currently Tesla vehicles do have
27:51
uh you know uh like the Gro cap, you can
27:54
like chat with it. We have our own audio
27:56
model that's not meant for natural
27:58
language interaction right now. more for
28:00
you know understanding the noises around
28:02
the car like sirens and emergency
28:04
vehicles and such. Uh but in the future
28:06
yeah you we will have fully integrated
28:09
uh voice uh control commands um that can
28:13
control the vehicle. It's just a bit too
28:15
early for that. You know you want to it
28:16
opens up an entire um uh area of like
28:21
testing that we got to do. For example,
28:23
you shouldn't be able to tell the car to
28:24
crash and then you shouldn't crash it.
28:26
There's a lot of uh safety that needs to
28:28
be done to protect against adversary
28:30
attacks using voice. Uh and it's just
28:32
like not worth the trouble right now.
28:42
Uh so in terms of uh like understanding
28:46
the physical world around uh like what's
28:48
happening so you mentioned that you're
28:50
using like gossian splatting. So are is
28:52
Tesla mainly working on improving those
28:55
models to give better visual perception?
28:58
Is that the kind of things you're
28:59
working on in terms of interpretability?
29:02
Yeah, that's one of the many things I I
29:04
listed like four or five things, but
29:05
yeah, it's like some 3D understanding
29:07
using caution splats or other forms of
29:10
3D understanding.
29:11
So what are some other examples?
29:13
For example, like the 3D locations of
29:15
vehicles, their shapes, their future
29:17
predictions, a lot of such things. Yeah.
29:22
Let's thank Ashok one last time.
29:25
[applause]]