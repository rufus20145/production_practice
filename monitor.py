"""
API для отслеживания изменений объектов. Для работы необходимо передать
в конструктор строку с URL в формате SQLAlchemy, либо имя файла, в котором
находятся параметры, необходимые для подключения к базе данных.
При вызове метода получения обновлений ранее метода получения
начального состояния правильная работа не гарантируется.
"""
from enum import Enum
import json
import logging as log
from typing import Callable, Optional

import sqlalchemy as sa
from errors import WrongStateError

from model.base import Alchemy
from model.model import Entity, EntityEncoder, Patch, PatchEncoder

func: Callable


class ChangeMonitor:
    """
    Класс ChangeMonitor предоставляет API для отслеживания изменений объектов.

    Для работы с классом необходимо передать в конструктор строку с URL в формате SQLAlchemy,
    либо имя файла, в котором находятся параметры, необходимые для подключения к базе данных.

    При вызове метода получения обновлений (get_update) ранее метода получения начального состояния
    (get_initial_state) правильная работа не гарантируется.

    Args:
        filename (Optional[str]): Имя файла, содержащего параметры для подключения к базе данных.
        dburl (Optional[str]): URL в формате SQLAlchemy для подключения к базе данных.
    """

    _max_record_id = 0
    _cache: "dict[int, Entity]" = {}
    _alch: Alchemy

    def __init__(
        self,
        filename: Optional[str] = None,
        dburl: Optional[str] = None,
    ):
        """
        Конструктор класса ChangeMonitor.

        Args:
            filename (Optional[str]): Имя файла, содержащего параметры для подключения к базе данных.
            dburl (Optional[str]): URL в формате SQLAlchemy для подключения к базе данных.

        """
        self._alch = Alchemy(dburl=dburl, filename=filename)
        self._state = States.INITIALIZED

        log.info("Initialized change monitor")

    def get_initial_state(self) -> str:
        """
        Получает начальное состояние объектов.

        Returns:
            str: JSON-представление начального состояния объектов.

        Raises:
            WrongStateError: Если метод вызывается не после инициализации объекта ChangeMonitor.
        """
        if self._state is not States.INITIALIZED:
            raise WrongStateError(
                "Can`t get initial state, because state is %s" % self._state
            )

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
        try:
            return json.dumps(self._cache, cls=EntityEncoder)
        finally:
            self._state = States.GOT_INITIAL_STATE

    def get_update(self) -> str:
        """
        Получает обновления объектов.

        Returns:
            str: JSON-представление списка обновлений объектов.

        Raises:
            WrongStateError: Если метод вызывается до того, как был получен начальный состояние методом get_initial_state.
        """
        if self._state is not States.GOT_INITIAL_STATE:
            raise WrongStateError(
                "Can`t get update, because you didn`t call get_initial_state"
            )

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


class States(Enum):
    """
    Перечисление States представляет возможные состояния объекта ChangeMonitor.

    INITIALIZED: Состояние, когда объект инициализирован и готов к получению начального состояния.
    GOT_INITIAL_STATE: Состояние, когда объект получил начальное состояние и готов к получению обновлений.

    """

    INITIALIZED = 0
    GOT_INITIAL_STATE = 1
