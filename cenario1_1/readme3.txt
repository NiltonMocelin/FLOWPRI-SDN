O arquivo controlnet.py se refere a uma topologia onde o controlador roda sobre mininet hosts.
ref: https://mailman.stanford.edu/pipermail/mininet-discuss/2016-February/006753.html

> examples/controlnet.py demonstrates one approach for running controllers
> in Mininet hosts
>
> However:
>
> 0. It may not be the best design or most straightforward example.
> 1. It’s out-of-band rather than in-band control. (It would be nice for
> someone to make an in-band example.)
> 2. The switches are still in the root namespace, since it was intended to
> be usable with OVSSwitch(…inNamespace=False)
> 3. OVSSwitch(…inNamespace=True) is still work in progress.
>
> The behavior you describe is what you should be expecting (I hope so at
> least!) - by default, the data network isn’t connected to the
> control/management network, and the switches are controlled by the
> controller.
>
> You will probably want to think very carefully and precisely about what
> you are trying to model, how it would work, and how to model it in Mininet,
> but this may help.
>
>



Outros exemplos em sshd.py e hwintf.py
