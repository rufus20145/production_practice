"""
TODO module docstring 
"""
import json
import logging as log

from sqlalchemy import and_, func

from alchemy.base import Alchemy
from alchemy.objects import Entity, EntityEncoder
from errors import ParameterError
from model.patch_object import Patch, PatchEncoder

func: callable


class ChangeMonitor:
    """
    TODO class docstring
    """

    _max_record_id = 0
    _cache: "dict[int, Entity]" = {}
    _alch: Alchemy

    def __init__(self, filename: str = None, dburl: str = None):
        if dburl:
            self._alch = Alchemy(dburl=dburl)
        elif filename:
            self._alch = Alchemy(filename=filename)
        else:
            raise ParameterError("No dburl nor filename specified.")

        log.info("Initialized")

    def get_initial_state(self) -> str:
        """
        TODO docstring
        """

        with self._alch.session_factory() as session:
            subq = (
                session.query(
                    Entity.entity_id, func.max(Entity.record_id).label("max_record_id")
                )
                .group_by(Entity.entity_id)
                .subquery("t2")
            )
            query = (
                session.query(Entity)
                .join(
                    subq,
                    and_(
                        Entity.entity_id == subq.c.entity_id,
                        Entity.record_id == subq.c.max_record_id,
                    ),
                )
                .order_by(Entity.entity_id)
            )
            entites = query.all()

        for entity in entites:
            if entity.record_id > self._max_record_id:
                self._max_record_id = entity.record_id
            self._cache[entity.entity_id] = entity

        log.info("Max record id after initial state: %d", self._max_record_id)
        return json.dumps(self._cache, cls=EntityEncoder)

    def get_update(self) -> str:
        """
        TODO docstring
        """
        patch_list: list[Patch] = []

        with self._alch.session_factory() as session:
            query = (
                session.query(Entity)
                .filter(Entity.record_id > self._max_record_id)
                .order_by(Entity.record_id)
            )
            entites = query.all()

        for entity in entites:
            if entity.record_id > self._max_record_id:
                self._max_record_id = entity.record_id

            if entity.entity_id not in self._cache:
                self._cache[entity.entity_id] = entity
                patch_list.append(
                    Patch(
                        op="add",
                        path=f"/{entity.entity_id}",
                        value=json.dumps(entity, cls=EntityEncoder),
                    )
                )
            else:
                entity_old = self._cache[entity.entity_id]
                # TODO сделать обход всех полей по списку для устранения дублирования
                if entity.foo != entity_old.foo:
                    patch_list.append(
                        Patch(
                            path=f"/{entity.entity_id}/foo",
                            value=entity.foo,
                        )
                    )
                if entity.bar != entity_old.bar:
                    patch_list.append(
                        Patch(
                            path=f"/{entity.entity_id}/bar",
                            value=entity.bar,
                        )
                    )

        log.info("Max record id after patch: %d", self._max_record_id)
        return json.dumps(patch_list, cls=PatchEncoder)
