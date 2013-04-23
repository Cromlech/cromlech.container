# -*- coding: utf-8 -*-

from .interfaces import IContainerModifiedEvent
from zope.interface import implementer, alsoProvides
from zope.event import notify
from zope.location import LocationProxy
from zope.location.interfaces import IContained, ILocation, ISublocations
from zope.lifecycleevent import (
    ObjectModifiedEvent, ObjectMovedEvent,
    ObjectAddedEvent, ObjectRemovedEvent)


@implementer(IContained)
class Contained(object):
    """Stupid mix-in that defines `__parent__` and `__name__` attributes.
    """

    __parent__ = __name__ = None


@implementer(IContained)
class ContainedProxy(LocationProxy):
    pass


@implementer(IContainerModifiedEvent)
class ContainerModifiedEvent(ObjectModifiedEvent):
    """The container has been modified.
    """
    pass


@implementer(ISublocations)
class ContainerSublocations(object):
    """Basic implementation of an `ISublocations`
    """

    def __init__(self, container):
        self.container = container

    def sublocations(self):
        container = self.container
        for key in container:
            yield container[key]


def containedEvent(object, container, name=None):
    """Establish the containment of the object in the container.
    """
    if not IContained.providedBy(object):
        if ILocation.providedBy(object):
            alsoProvides(object, IContained)
        else:
            object = ContainedProxy(object)

    oldparent = object.__parent__
    oldname = object.__name__

    if oldparent is container and oldname == name:
        # No events
        return object, None

    object.__parent__ = container
    object.__name__ = name

    if oldparent is None or oldname is None:
        event = ObjectAddedEvent(object, container, name)
    else:
        event = ObjectMovedEvent(object, oldparent, oldname, container, name)

    return object, event


def contained(object, container, name=None):
    """Establishes the containment of the object in the container
    """
    return containedEvent(object, container, name)[0]


def notifyContainerModified(object, *descriptions):
    """Notifies that the container was modified.
    """
    notify(ContainerModifiedEvent(object, *descriptions))


def setitem(container, setitemf, name, object):
    """Helper function to set an item and generate needed events

    This helper is needed, in part, because the events need to get
    published after the `object` has been added to the `container`.
    """
    # Do basic name check:
    if isinstance(name, str):
        try:
            name = unicode(name)
        except UnicodeError:
            raise TypeError("name not unicode or ascii string")
    elif not isinstance(name, unicode):
        raise TypeError("name not unicode or ascii string")

    if not name:
        raise ValueError("empty names are not allowed")

    old = container.get(name)
    if old is object:
        return
    if old is not None:
        raise KeyError(name)

    object, event = containedEvent(object, container, name)
    setitemf(name, object)
    if event:
        notify(event)
        notifyContainerModified(container)


fixing_up = False


def uncontained(object, container, name=None):
    try:
        oldparent = object.__parent__
        oldname = object.__name__
    except AttributeError:
        # The old object doesn't implements IContained
        # Maybe we're converting old data:
        if not fixing_up:
            raise
        oldparent = None
        oldname = None

    if oldparent is not container or oldname != name:
        if oldparent is not None or oldname is not None:
            notifyContainerModified(container)
        return

    event = ObjectRemovedEvent(object, oldparent, oldname)
    notify(event)

    try:
        object.__parent__ = None
        object.__name__ = None
    except AttributeError:
        # This should catch problems from broken objects
        pass

    notifyContainerModified(container)
