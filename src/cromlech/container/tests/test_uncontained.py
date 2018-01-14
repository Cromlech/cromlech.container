# -*- coding: utf-8 -*-
"""Clear the containment relationship between the `object` and
the `container`.
"""

from cromlech.container.contained import Contained, containedEvent, uncontained
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent


class Item(Contained):
    pass


def test_uncontained(events):
    item = Item()
    container = {u'foo': item}
    x, event = containedEvent(item, container, u'foo')

    assert item.__parent__ is container
    assert item.__name__ == u'foo'

    uncontained(item, container, u'foo')
    assert item.__parent__ is None
    assert item.__name__ is None

    assert len(events) == 2

    event = events.popleft()
    assert event.object is item
    assert event.oldParent is container
    assert event.oldName == u'foo'
    assert event.newParent is None
    assert event.newName is None

    event = events.popleft()
    assert event.object is container

    # Events are never triggered twice
    uncontained(item, container, u'foo')
    assert not len(events)

    # Name changed, uncontain will just trigger a modification
    # on the container
    item.__parent__, item.__name__ = container, None
    uncontained(item, container, u'foo')
    event = events.pop()
    assert IObjectModifiedEvent.providedBy(event)

    # Name and parent changed, uncontain will just trigger a modification
    # on the container
    item.__parent__, item.__name__ = None, u'bar'
    uncontained(item, container, u'foo')
    event = events.pop()
    assert IObjectModifiedEvent.providedBy(event)
