import json
from aiohttp import web
from models import engine, Base, Adv, Session
from schema import CreateAdv, PatchAdv, VALIDATION_CLASS
from pydantic import ValidationError


async def orm_context(app):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request['session'] = session
        response = await handler(request)
        return response


class HttpError(Exception):  # Класс для обработки ошибок
    def __init__(self, status_code: int, message: dict | list | str):
        self.status_code = status_code
        self.message = message


def validation_json(json_data: dict, validation_model: VALIDATION_CLASS):
    try:
        model_object = validation_model(**json_data)
        model_object_dict = model_object.dict(exclude_none=True)
    except ValidationError as err:
        raise HttpError(400, message=err.errors())
    return model_object_dict


async def get_adv(adv_id: int, session: Session) -> Adv:  # получить объявление из БД
    adv = await session.get(Adv, adv_id)
    if adv is None:
        raise web.HTTPNotFound(
            text=json.dumps({'error': 'adv not found'}),
            content_type='application/json'
        )
    return adv


class AdvView(web.View):

    @property
    def session(self) -> Session:
        return self.request['session']

    @property
    def adv_id(self) -> int:
        return int(self.request.match_info['adv_id'])

    async def get(self):
        adv = await get_adv(self.adv_id, self.session)
        return web.json_response({
            'id': adv.id,
            'title': adv.title,
            'description': adv.description,
            'created_at': int(adv.created_at.timestamp()),
            'author': adv.author
        })

    async def post(self):
        raw_json_data = await self.request.json()
        json_data = validation_json(raw_json_data, CreateAdv)
        adv = Adv(**json_data)
        self.session.add(adv)
        await self.session.commit()
        return web.json_response({
            'id': adv.id
        })

    async def patch(self):
        raw_json_data = await self.request.json()
        json_data = validation_json(raw_json_data, PatchAdv)
        adv = await get_adv(self.adv_id, self.session)
        for field, value in json_data.items():
            setattr(adv, field, value)
        self.session.add(adv)
        await self.session.commit()
        return web.json_response({
            'id': adv.id
        })

    async def delete(self):
        adv = await get_adv(self.adv_id, self.session)
        await self.session.delete(adv)
        await self.session.commit()
        return web.json_response({
            'id': adv.id
        })


async def get_app():
    app = web.Application()
    app.add_routes([web.get('/adv/{adv_id:\d+}', AdvView),
                    web.patch('/adv/{adv_id:\d+}', AdvView),
                    web.delete('/adv/{adv_id:\d+}', AdvView),
                    web.post('/adv/', AdvView)
                    ])
    app.cleanup_ctx.append(orm_context)
    app.middlewares.append(session_middleware)

    return app

if __name__ == '__main__':
    app = get_app()
    web.run_app(app)





