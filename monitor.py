"""
API для отслеживания изменений объектов. Для работы необходимо передать
в конструктор строку с URL в формате SQLAlchemy, либо имя файла, в котором
находятся параметры, необходимые для подключения к базе данных.
При вызове метода получения обновлений ранее метода получения
начального состояния правильная работа не гарантируется.
"""
import json
import logging as log

import sqlalchemy as sa

from model.base import Alchemy
from model.model import Entity, EntityEncoder, Patch, PatchEncoder

func: callable


class ChangeMonitor:
    _max_record_id = 0
    _cache: "dict[int, Entity]" = {}
    _alch: Alchemy

    def __init__(
        self,
        filename: str = None,
        dburl: str = None,
    ):
        self._alch = Alchemy(dburl=dburl, filename=filename)

        log.info("Initialized")

    def get_initial_state(self) -> str:
        with self._alch.get_session() as session:
            subq = (
                sa.select(
                    Entity.entity_id,
                    sa.func.max(Entity.record_id).label("max_record_id"),
                )
                .group_by(Entity.entity_id)
                .subquery("t2")
            )
            query = (
                sa.select(Entity)
                .join(
                    subq,
                    sa.and_(
                        Entity.record_id == subq.c.max_record_id,
                    ),
                )
                .order_by(Entity.entity_id)
            )

            result = session.scalars(query)
            entites = result.all()

        for entity in entites:
            if entity.record_id > self._max_record_id:
                self._max_record_id = entity.record_id
            self._cache[entity.entity_id] = entity

        log.info("Max record id after initial state: %d", self._max_record_id)
        log.debug("Number of entities: %d", len(entites))
        return json.dumps(self._cache, cls=EntityEncoder)

    def get_update(self) -> str:
        patch_list: "list[Patch]" = []

        with self._alch.get_session() as session:
            query = (
                sa.select(Entity)
                .filter(Entity.record_id > self._max_record_id)
                .order_by(Entity.record_id)
            )

            result = session.scalars(query)
            entities = result.all()

        for entity in entities:
            if entity.record_id > self._max_record_id:
                self._max_record_id = entity.record_id

            if entity.entity_id not in self._cache:
                self._cache[entity.entity_id] = entity
                patch_list.append(
                    Patch(
                        operation="add",
                        path=f"/{entity.entity_id}",
                        value=json.dumps(entity, cls=EntityEncoder),
                    )
                )
            else:
                entity_old = self._cache[entity.entity_id]
                for field in Entity.relevant_atributes:
                    if getattr(entity, field) != getattr(entity_old, field):
                        patch_list.append(
                            Patch(
                                path=f"/{entity.entity_id}/{field}",
                                value=getattr(entity, field),
                            )
                        )

        log.info("Max record id after patch: %d", self._max_record_id)
        return json.dumps(patch_list, cls=PatchEncoder)
