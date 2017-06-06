from .auth_route import user
from .news_route import news, tags

blueprints = {
    '/user': auth,
    '/news': news
}
